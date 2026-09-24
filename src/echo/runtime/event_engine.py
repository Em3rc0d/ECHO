"""Temporal event consolidation for ECHO runtime.

The engine converts per-window model scores into stable acoustic events. It has
no ML dependency and intentionally requires threshold parameters from upstream
calibration/configuration rather than embedding unvalidated production values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from statistics import fmean
from typing import Mapping
from uuid import NAMESPACE_URL, uuid5


@dataclass(frozen=True)
class ThresholdConfig:
    on_threshold: float
    off_threshold: float
    confirm_windows: int
    release_windows: int
    cooldown_seconds: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.off_threshold <= self.on_threshold <= 1.0:
            raise ValueError("require 0 <= off_threshold <= on_threshold <= 1")
        if self.confirm_windows < 1:
            raise ValueError("confirm_windows must be >= 1")
        if self.release_windows < 1:
            raise ValueError("release_windows must be >= 1")
        if self.cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must be >= 0")


@dataclass(frozen=True)
class RawInference:
    source_id: str
    site_id: str
    stream_session_id: str
    window_start_utc: datetime
    window_end_utc: datetime
    scores: Mapping[str, float]
    model_version: str

    def __post_init__(self) -> None:
        if not self.source_id or not self.site_id or not self.stream_session_id:
            raise ValueError("source_id, site_id and stream_session_id are required")
        if not self.model_version:
            raise ValueError("model_version is required")
        for name, value in self.scores.items():
            score = float(value)
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"score for {name!r} must be within [0, 1]")
        for name, value in (
            ("window_start_utc", self.window_start_utc),
            ("window_end_utc", self.window_end_utc),
        ):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.window_end_utc < self.window_start_utc:
            raise ValueError("window_end_utc cannot precede window_start_utc")


@dataclass(frozen=True)
class ConfirmedEvent:
    event_id: str
    source_id: str
    site_id: str
    event_type: str
    onset_utc: datetime
    end_utc: datetime | None
    confidence_peak: float
    confidence_mean: float
    model_version: str
    threshold_version: str
    stream_session_id: str
    lifecycle: str
    evidence_windows: int

    def to_dict(self) -> dict:
        return {
            "schema_version": "echo.event.v1",
            "event_id": self.event_id,
            "source_id": self.source_id,
            "site_id": self.site_id,
            "event_type": self.event_type,
            "onset_utc": self.onset_utc.astimezone(timezone.utc).isoformat(),
            "end_utc": (
                self.end_utc.astimezone(timezone.utc).isoformat()
                if self.end_utc is not None
                else None
            ),
            "confidence": {
                "peak": self.confidence_peak,
                "mean": self.confidence_mean,
            },
            "model_version": self.model_version,
            "threshold_version": self.threshold_version,
            "stream_session_id": self.stream_session_id,
            "provenance": {
                "event_engine": "echo.temporal-event-engine.v1",
                "lifecycle": self.lifecycle,
                "evidence_windows": self.evidence_windows,
            },
        }


@dataclass
class _LabelState:
    candidate_count: int = 0
    candidate_onset: datetime | None = None
    candidate_scores: list[float] = field(default_factory=list)

    active_event_id: str | None = None
    active_onset: datetime | None = None
    active_scores: list[float] = field(default_factory=list)
    active_model_version: str | None = None
    release_count: int = 0

    cooldown_until: datetime | None = None

    def reset_candidate(self) -> None:
        self.candidate_count = 0
        self.candidate_onset = None
        self.candidate_scores.clear()

    def reset_active(self) -> None:
        self.active_event_id = None
        self.active_onset = None
        self.active_scores.clear()
        self.active_model_version = None
        self.release_count = 0


class TemporalEventEngine:
    """Stateful per-source/per-session event consolidation."""

    def __init__(
        self,
        *,
        thresholds: Mapping[str, ThresholdConfig],
        threshold_version: str,
    ) -> None:
        if not thresholds:
            raise ValueError("at least one threshold config is required")
        if not threshold_version:
            raise ValueError("threshold_version is required")
        self._thresholds = dict(thresholds)
        self._threshold_version = threshold_version
        self._states: dict[tuple[str, str, str], _LabelState] = {}

    def _state(self, inference: RawInference, label: str) -> _LabelState:
        key = (inference.source_id, inference.stream_session_id, label)
        return self._states.setdefault(key, _LabelState())

    @staticmethod
    def _event_id(
        *,
        source_id: str,
        stream_session_id: str,
        label: str,
        onset: datetime,
    ) -> str:
        material = (
            f"echo:event:{source_id}:{stream_session_id}:{label}:"
            f"{onset.astimezone(timezone.utc).isoformat()}"
        )
        return str(uuid5(NAMESPACE_URL, material))

    def _event(
        self,
        *,
        inference: RawInference,
        label: str,
        state: _LabelState,
        lifecycle: str,
        end_utc: datetime | None,
    ) -> ConfirmedEvent:
        if not state.active_event_id or state.active_onset is None:
            raise RuntimeError("active event state is incomplete")
        if not state.active_scores:
            raise RuntimeError("active event has no score evidence")
        return ConfirmedEvent(
            event_id=state.active_event_id,
            source_id=inference.source_id,
            site_id=inference.site_id,
            event_type=label,
            onset_utc=state.active_onset,
            end_utc=end_utc,
            confidence_peak=max(state.active_scores),
            confidence_mean=fmean(state.active_scores),
            model_version=state.active_model_version or inference.model_version,
            threshold_version=self._threshold_version,
            stream_session_id=inference.stream_session_id,
            lifecycle=lifecycle,
            evidence_windows=len(state.active_scores),
        )

    def close_session(
        self,
        *,
        source_id: str,
        site_id: str,
        stream_session_id: str,
        end_utc: datetime,
        model_version: str,
    ) -> list[ConfirmedEvent]:
        """Close every active event for one stream session at EOF/disconnect.

        Candidate-only evidence is discarded because it never reached the
        configured confirmation rule. Confirmed events retain their event_id and
        are emitted once with lifecycle=CLOSED.
        """

        if end_utc.tzinfo is None or end_utc.utcoffset() is None:
            raise ValueError("end_utc must be timezone-aware")
        outputs: list[ConfirmedEvent] = []
        for label in self._thresholds:
            key = (source_id, stream_session_id, label)
            state = self._states.get(key)
            if state is None:
                continue
            if state.active_event_id is not None:
                synthetic = RawInference(
                    source_id=source_id,
                    site_id=site_id,
                    stream_session_id=stream_session_id,
                    window_start_utc=end_utc,
                    window_end_utc=end_utc,
                    scores={label: state.active_scores[-1]},
                    model_version=state.active_model_version or model_version,
                )
                outputs.append(
                    self._event(
                        inference=synthetic,
                        label=label,
                        state=state,
                        lifecycle="CLOSED",
                        end_utc=end_utc,
                    )
                )
            state.reset_active()
            state.reset_candidate()
            self._states.pop(key, None)
        return outputs

    def ingest(self, inference: RawInference) -> list[ConfirmedEvent]:
        outputs: list[ConfirmedEvent] = []

        for label, cfg in self._thresholds.items():
            score = float(inference.scores.get(label, 0.0))
            state = self._state(inference, label)

            if state.active_event_id is not None:
                state.active_scores.append(score)
                if score < cfg.off_threshold:
                    state.release_count += 1
                else:
                    state.release_count = 0

                if state.release_count >= cfg.release_windows:
                    outputs.append(
                        self._event(
                            inference=inference,
                            label=label,
                            state=state,
                            lifecycle="CLOSED",
                            end_utc=inference.window_end_utc,
                        )
                    )
                    state.cooldown_until = inference.window_end_utc + timedelta(
                        seconds=cfg.cooldown_seconds
                    )
                    state.reset_active()
                    state.reset_candidate()
                continue

            if (
                state.cooldown_until is not None
                and inference.window_start_utc < state.cooldown_until
            ):
                state.reset_candidate()
                continue

            if score >= cfg.on_threshold:
                if state.candidate_count == 0:
                    state.candidate_onset = inference.window_start_utc
                    state.candidate_scores = []
                state.candidate_count += 1
                state.candidate_scores.append(score)

                if state.candidate_count >= cfg.confirm_windows:
                    if state.candidate_onset is None:
                        raise RuntimeError("candidate onset missing at confirmation")
                    state.active_onset = state.candidate_onset
                    state.active_event_id = self._event_id(
                        source_id=inference.source_id,
                        stream_session_id=inference.stream_session_id,
                        label=label,
                        onset=state.active_onset,
                    )
                    state.active_scores = list(state.candidate_scores)
                    state.active_model_version = inference.model_version
                    state.release_count = 0
                    state.reset_candidate()
                    outputs.append(
                        self._event(
                            inference=inference,
                            label=label,
                            state=state,
                            lifecycle="CONFIRMED",
                            end_utc=None,
                        )
                    )
            else:
                state.reset_candidate()

        return outputs
