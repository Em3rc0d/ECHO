"""End-to-end replay pipeline: audio -> scores -> events -> publisher."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
from typing import Iterable, Protocol

from echo.modeling.audio import decode_audio_f32_mono

from .event_engine import RawInference, TemporalEventEngine
from .replay import iter_replay_windows


class WindowScorer(Protocol):
    sample_rate_hz: int
    model_version: str

    def score(self, waveform) -> dict[str, float]:
        ...


class EventPublisher(Protocol):
    def publish(self, event) -> None:
        ...


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class EchoReplayPipeline:
    def __init__(
        self,
        *,
        scorer: WindowScorer,
        event_engine: TemporalEventEngine,
        publishers: Iterable[EventPublisher],
    ) -> None:
        self.scorer = scorer
        self.event_engine = event_engine
        self.publishers = list(publishers)
        if not self.publishers:
            raise ValueError("at least one event publisher is required")

    def run_file(
        self,
        path: str | Path,
        *,
        source_id: str,
        site_id: str,
        window_seconds: float,
        hop_seconds: float,
        start_utc: datetime | None = None,
        ffmpeg_bin: str = "ffmpeg",
    ) -> dict[str, int | str]:
        source = Path(path)
        if start_utc is None:
            start_utc = datetime(2000, 1, 1, tzinfo=timezone.utc)
        if start_utc.tzinfo is None or start_utc.utcoffset() is None:
            raise ValueError("start_utc must be timezone-aware")

        media_sha = file_sha256(source)
        stream_session_id = f"replay:{media_sha[:24]}"
        waveform = decode_audio_f32_mono(
            source,
            sample_rate_hz=self.scorer.sample_rate_hz,
            ffmpeg_bin=ffmpeg_bin,
        )

        window_count = 0
        event_messages = 0
        last_window_end_utc = start_utc
        for window in iter_replay_windows(
            waveform,
            sample_rate_hz=self.scorer.sample_rate_hz,
            window_seconds=window_seconds,
            hop_seconds=hop_seconds,
            pad_final=False,
        ):
            window_count += 1
            scores = self.scorer.score(window.waveform)
            last_window_end_utc = start_utc + timedelta(
                seconds=window.end_sample / self.scorer.sample_rate_hz
            )
            inference = RawInference(
                source_id=source_id,
                site_id=site_id,
                stream_session_id=stream_session_id,
                window_start_utc=start_utc
                + timedelta(
                    seconds=window.start_sample / self.scorer.sample_rate_hz
                ),
                window_end_utc=last_window_end_utc,
                scores=scores,
                model_version=self.scorer.model_version,
            )
            for event in self.event_engine.ingest(inference):
                payload = event.to_dict()
                for publisher in self.publishers:
                    publisher.publish(payload)
                event_messages += 1

        if window_count:
            for event in self.event_engine.close_session(
                source_id=source_id,
                site_id=site_id,
                stream_session_id=stream_session_id,
                end_utc=last_window_end_utc,
                model_version=self.scorer.model_version,
            ):
                payload = event.to_dict()
                for publisher in self.publishers:
                    publisher.publish(payload)
                event_messages += 1

        return {
            "source_id": source_id,
            "site_id": site_id,
            "stream_session_id": stream_session_id,
            "media_sha256": media_sha,
            "window_count": window_count,
            "event_message_count": event_messages,
        }
