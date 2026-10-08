#!/usr/bin/env python3
"""ECHO professor demo adapter.

This adapter intentionally does not implement alternate classification logic.
It loads the selected ECHO MVP model and current temporal Event Engine
configuration and routes audio through EchoReplayPipeline. Governed controlled
scenarios publish the same echo.event.v1 payloads over MQTT QoS 1. External
microphone/WAV audio is diagnostic-only under ECHO-DEMO-ABSTENTION-v1:
unvalidated target candidates can be displayed but are not published as
accepted target events.

The demo is a presentation/robustness surface, not an alternate inference path.
"""

from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import tempfile
import threading
from urllib.parse import urlparse
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echo.modeling.inference import CompactCnnScorer, EmbeddingHeadScorer
from echo.runtime.event_engine import TemporalEventEngine, ThresholdConfig
from echo.runtime.pipeline import EchoReplayPipeline
from echo.runtime.publishers import MqttEventPublisher


DISPLAY = {
    "GLASS_SHATTER": "Rotura de vidrio",
    "SIREN": "Sirena",
    "VEHICLE_HORN": "Bocina vehicular",
}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_RECORDING_SECONDS = 30

SCENARIO_LABELS = {
    "glass_shatter": "Rotura de vidrio",
    "siren": "Sirena",
    "vehicle_horn": "Bocina vehicular",
    "negative": "Ambiente sin evento objetivo",
}


class CollectingPublisher:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def publish(self, event) -> None:
        self.events.append(dict(event))


class TracingScorer:
    """Collect per-window scores without retaining raw audio."""

    def __init__(self, scorer) -> None:
        self._scorer = scorer
        self.sample_rate_hz = scorer.sample_rate_hz
        self.model_version = scorer.model_version
        self.rows: list[dict[str, float]] = []

    def score(self, waveform) -> dict[str, float]:
        scores = {
            str(label): float(value)
            for label, value in self._scorer.score(waveform).items()
        }
        self.rows.append(scores)
        return scores


def summarize_score_trace(
    rows: list[dict[str, float]],
    thresholds: dict[str, ThresholdConfig],
) -> dict:
    labels = {}
    for label, cfg in thresholds.items():
        values = [float(row.get(label, 0.0)) for row in rows]
        longest = 0
        current = 0
        for value in values:
            if value >= cfg.on_threshold:
                current += 1
                longest = max(longest, current)
            else:
                current = 0
        labels[label] = {
            "on_threshold": cfg.on_threshold,
            "max_score": max(values) if values else 0.0,
            "mean_score": (sum(values) / len(values)) if values else 0.0,
            "windows_at_or_above_on": sum(
                1 for value in values if value >= cfg.on_threshold
            ),
            "longest_consecutive_at_or_above_on": longest,
        }
    ranked = sorted(
        (
            {
                "event_type": label,
                "display_name": DISPLAY.get(label, label),
                **row,
            }
            for label, row in labels.items()
        ),
        key=lambda row: row["max_score"],
        reverse=True,
    )
    return {
        "window_count": len(rows),
        "labels": labels,
        "ranked_labels": ranked,
        "raw_audio_retained": False,
        "diagnostic_kind": "SCORE_TRACE_NOT_EMBEDDING_DISTANCE_OOD",
    }


def external_abstention_decision(
    *,
    candidate_events: list[dict],
    candidate_labels: list[str],
    score_diagnostics: dict | None,
) -> dict:
    """Conservative demo-only rejection boundary for uncalibrated external audio.

    This is intentionally not presented as a learned OOD detector. Until ECHO has
    a field-calibrated acceptance profile, external audio may expose internal target
    candidates for diagnosis but cannot promote them to accepted target events.
    """

    if not candidate_labels:
        return {
            "version": "ECHO-DEMO-ABSTENTION-v1",
            "state": "NO_TARGET",
            "accepted_target": None,
            "publish_target_event": False,
            "candidate_labels": [],
            "candidate_event_count": 0,
            "ood_status": "NO_TARGET_EVIDENCE",
            "rationale": (
                "The calibrated temporal engine did not confirm any current target "
                "class on this external recording."
            ),
            "diagnostic_kind": (
                (score_diagnostics or {}).get("diagnostic_kind")
                or "SCORE_TRACE_NOT_EMBEDDING_DISTANCE_OOD"
            ),
        }

    ranked = sorted(
        candidate_events,
        key=lambda row: float(row.get("confidence_peak") or 0.0),
        reverse=True,
    )
    top = ranked[0] if ranked else None
    return {
        "version": "ECHO-DEMO-ABSTENTION-v1",
        "state": "UNKNOWN",
        "accepted_target": None,
        "publish_target_event": False,
        "candidate_labels": candidate_labels,
        "candidate_event_count": len(candidate_events),
        "top_candidate": (
            {
                "event_type": top.get("event_type"),
                "display_name": top.get("display_name"),
                "confidence_peak": float(top.get("confidence_peak") or 0.0),
                "confidence_mean": float(top.get("confidence_mean") or 0.0),
            }
            if top is not None
            else None
        ),
        "ood_status": "EXTERNAL_DOMAIN_UNCALIBRATED",
        "rationale": (
            "One or more target heads produced temporally confirmed candidates, "
            "but external microphone/WAV audio has no field-calibrated acceptance "
            "or learned OOD profile yet. ECHO abstains instead of emitting a target "
            "event."
        ),
        "diagnostic_kind": (
            (score_diagnostics or {}).get("diagnostic_kind")
            or "SCORE_TRACE_NOT_EMBEDDING_DISTANCE_OOD"
        ),
    }


def load_thresholds(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    labels = payload.get("labels") or {}
    thresholds = {
        str(label): ThresholdConfig(
            on_threshold=float(row["on_threshold"]),
            off_threshold=float(row["off_threshold"]),
            confirm_windows=int(row["confirm_windows"]),
            release_windows=int(row["release_windows"]),
            cooldown_seconds=float(row.get("cooldown_seconds", 0.0)),
        )
        for label, row in labels.items()
    }
    return payload, str(payload["threshold_version"]), thresholds


def resolve_checkpoint(raw: str, *, selection: Path, benchmark: str) -> Path:
    path = Path(raw)
    candidates = [path]
    if not path.is_absolute():
        candidates.append((ROOT / path).resolve())
    folder_by_benchmark = {
        "YAMNET_EMBEDDINGS_HEAD": "yamnet",
        "PANNS_CNN14_HEAD": "panns",
        "COMPACT_LOGMEL_CNN": "compact-cnn",
    }
    filename = Path(str(raw).replace("\\", "/")).name
    folder = folder_by_benchmark.get(benchmark)
    if folder:
        candidates.append(selection.resolve().parent / folder / filename)
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        "selected checkpoint not found: "
        + ", ".join(str(candidate) for candidate in candidates)
    )


def resolve_fixture_wav(fixtures_path: Path, scenario: dict) -> Path:
    stored = Path(str(scenario.get("wav") or ""))
    candidates = [
        stored,
        fixtures_path.resolve().parent / "streams" / stored.name,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        f"fixture WAV not found for {scenario.get('scenario_id')}: "
        + ", ".join(str(candidate) for candidate in candidates)
    )


def build_scorer(selection_path: Path, panns_checkpoint: Path, device: str):
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    winner = selection["winner"]
    benchmark = str(winner["benchmark"])
    checkpoint = resolve_checkpoint(
        str(winner["checkpoint"]),
        selection=selection_path,
        benchmark=benchmark,
    )

    if benchmark == "PANNS_CNN14_HEAD":
        scorer = EmbeddingHeadScorer(
            checkpoint=checkpoint,
            backbone="panns",
            device=device,
            panns_checkpoint=str(panns_checkpoint),
        )
    elif benchmark == "YAMNET_EMBEDDINGS_HEAD":
        scorer = EmbeddingHeadScorer(
            checkpoint=checkpoint,
            backbone="yamnet",
            device=device,
        )
    elif benchmark == "COMPACT_LOGMEL_CNN":
        scorer = CompactCnnScorer(checkpoint=checkpoint, device=device)
    else:
        raise ValueError(f"unsupported selected benchmark: {benchmark}")
    return selection, benchmark, checkpoint, scorer


def choose_demo_scenarios(fixtures: dict, fixtures_path: Path) -> list[dict]:
    scenarios = fixtures.get("scenarios") or []
    preferred = [row for row in scenarios if row.get("partition") == "temporal_holdout"]
    if not preferred:
        preferred = [row for row in scenarios if row.get("partition") == "temporal_tune"]

    selected: list[dict] = []
    suffixes = (
        "burst-glass_shatter",
        "burst-siren",
        "burst-vehicle_horn",
        "negative",
    )
    for suffix in suffixes:
        row = next(
            (
                item
                for item in preferred
                if str(item.get("scenario_id") or "").endswith(suffix)
            ),
            None,
        )
        if row is None:
            continue
        scenario_id = str(row["scenario_id"])
        key = next((k for k in SCENARIO_LABELS if suffix.endswith(k)), suffix)
        expected = sorted(
            {
                label
                for event in (row.get("ground_truth") or [])
                for label in (event.get("labels") or [])
                if label in DISPLAY
            }
        )
        primary_expected = {
            "glass_shatter": "GLASS_SHATTER",
            "siren": "SIREN",
            "vehicle_horn": "VEHICLE_HORN",
            "negative": None,
        }.get(key)
        selected.append(
            {
                "scenario_id": scenario_id,
                "display_name": SCENARIO_LABELS.get(key, scenario_id),
                "partition": row.get("partition"),
                "duration_seconds": float(row.get("duration_seconds") or 0.0),
                "expected_labels": expected,
                "primary_expected_label": primary_expected,
                "ground_truth_event_count": len(row.get("ground_truth") or []),
                "wav": resolve_fixture_wav(fixtures_path, row),
            }
        )
    if len(selected) < 4:
        raise RuntimeError(
            "demo requires holdout/tune burst scenarios for glass, siren, horn and negative"
        )
    return selected


def aggregate_events(messages: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for payload in messages:
        event_id = str(payload["event_id"])
        lifecycle = str((payload.get("provenance") or {}).get("lifecycle") or "")
        row = grouped.setdefault(
            event_id,
            {
                "event_id": event_id,
                "event_type": payload.get("event_type"),
                "display_name": DISPLAY.get(
                    str(payload.get("event_type")),
                    str(payload.get("event_type")),
                ),
                "confidence_peak": 0.0,
                "confidence_mean": 0.0,
                "lifecycles": [],
                "onset_utc": payload.get("onset_utc"),
                "end_utc": payload.get("end_utc"),
            },
        )
        confidence = payload.get("confidence") or {}
        row["confidence_peak"] = max(
            float(row["confidence_peak"]),
            float(confidence.get("peak") or 0.0),
        )
        row["confidence_mean"] = max(
            float(row["confidence_mean"]),
            float(confidence.get("mean") or 0.0),
        )
        if lifecycle and lifecycle not in row["lifecycles"]:
            row["lifecycles"].append(lifecycle)
        if payload.get("end_utc"):
            row["end_utc"] = payload["end_utc"]
    return sorted(
        grouped.values(),
        key=lambda row: (str(row["event_type"]), str(row["event_id"])),
    )


class DemoApplication:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.fixtures_path = args.fixtures.resolve()
        self.fixtures = json.loads(self.fixtures_path.read_text(encoding="utf-8"))
        self.config_payload, self.threshold_version, self.thresholds = load_thresholds(
            args.event_config
        )
        (
            self.selection,
            self.benchmark,
            self.checkpoint,
            self.scorer,
        ) = build_scorer(
            args.selection,
            args.panns_checkpoint,
            args.device,
        )
        self.scenarios = choose_demo_scenarios(self.fixtures, self.fixtures_path)
        self.by_id = {row["scenario_id"]: row for row in self.scenarios}
        self.lock = threading.Lock()
        self.mqtt = MqttEventPublisher(
            host=args.mqtt_host,
            port=args.mqtt_port,
            topic=args.mqtt_topic,
            client_id="echo-professor-demo",
        )

    def close(self) -> None:
        self.mqtt.close()

    def status(self) -> dict:
        return {
            "profile_id": "ECHO-MVP-001",
            "mode": "CONTROLLED_VALIDATION_DEMO",
            "model_benchmark": self.benchmark,
            "threshold_version": self.threshold_version,
            "temporal_status": self.config_payload.get("status"),
            "field_calibrated": False,
            "mqtt_topic": self.args.mqtt_topic,
            "supported_events": list(DISPLAY),
            "user_wav_upload": True,
            "microphone_capture": True,
            "max_upload_bytes": MAX_UPLOAD_BYTES,
            "max_recording_seconds": MAX_RECORDING_SECONDS,
            "external_audio_policy": {
                "pad_final": False,
                "abstention_version": "ECHO-DEMO-ABSTENTION-v1",
                "target_event_publication": False,
                "min_duration_seconds": float(
                    self.config_payload.get("window_seconds") or 6.0
                ),
                "field_calibrated": False,
                "reason": (
                    "External demo audio disables zero-padded tail windows so a short "
                    "clip cannot manufacture repeated temporal evidence."
                ),
            },
        }

    def catalog(self) -> list[dict]:
        return [
            {
                key: value
                for key, value in row.items()
                if key != "wav"
            }
            | {"audio_url": f"/audio/{row['scenario_id']}"}
            for row in self.scenarios
        ]

    def _execute_audio(
        self,
        path: Path,
        *,
        source_id: str,
        external_audio: bool = False,
    ) -> dict:
        collector = CollectingPublisher()
        scorer = TracingScorer(self.scorer) if external_audio else self.scorer
        engine = TemporalEventEngine(
            thresholds=self.thresholds,
            threshold_version=self.threshold_version,
        )
        publishers = [collector] if external_audio else [collector, self.mqtt]
        pipeline = EchoReplayPipeline(
            scorer=scorer,
            event_engine=engine,
            publishers=publishers,
        )
        window_seconds = float(
            self.config_payload.get("window_seconds") or 6.0
        )
        with self.lock:
            summary = pipeline.run_file(
                path,
                source_id=source_id,
                site_id="ECHO-PROFESSOR-DEMO",
                window_seconds=window_seconds,
                hop_seconds=float(
                    self.config_payload.get("hop_seconds") or 1.0
                ),
                pad_final=not external_audio,
            )
        if external_audio and int(summary["window_count"]) == 0:
            raise ValueError(
                f"external demo audio must contain at least {window_seconds:.1f} "
                "seconds so ECHO can analyze one complete window without "
                "zero-padding repeated evidence"
            )
        logical_events = aggregate_events(collector.events)
        detected_labels = sorted(
            {
                str(row["event_type"])
                for row in logical_events
                if "CONFIRMED" in row["lifecycles"]
            }
        )
        return {
            "events": logical_events,
            "detected_labels": detected_labels,
            "event_message_count": len(collector.events),
            "logical_event_count": len(logical_events),
            "mqtt": {
                "published": bool(collector.events) and not external_audio,
                "message_count": 0 if external_audio else len(collector.events),
                "suppressed_by_abstention": bool(collector.events) and external_audio,
                "topic": self.args.mqtt_topic,
                "qos": 1,
            },
            "pipeline_summary": summary,
            "score_diagnostics": (
                summarize_score_trace(scorer.rows, self.thresholds)
                if external_audio
                else None
            ),
            "external_audio_policy": (
                {
                    "pad_final": False,
                    "min_duration_seconds": window_seconds,
                    "field_calibrated": False,
                }
                if external_audio
                else None
            ),
        }

    def run(self, scenario_id: str) -> dict:
        if scenario_id not in self.by_id:
            raise KeyError(scenario_id)
        scenario = self.by_id[scenario_id]
        execution = self._execute_audio(
            scenario["wav"],
            source_id=f"demo:{scenario_id}",
        )
        logical_events = execution["events"]
        detected_labels = execution["detected_labels"]
        expected_labels = list(scenario["expected_labels"])
        primary_expected = scenario.get("primary_expected_label")
        detected_set = set(detected_labels)
        if primary_expected:
            demo_outcome = (
                "EXPECTED_EVENT_DETECTED"
                if primary_expected in detected_set
                else "EXPECTED_EVENT_NOT_DETECTED"
            )
        else:
            demo_outcome = (
                "NO_TARGET_EVENT_DETECTED"
                if not detected_set
                else "UNEXPECTED_TARGET_EVENT_DETECTED"
            )
        return {
            "scenario_id": scenario_id,
            "display_name": scenario["display_name"],
            "partition": scenario["partition"],
            "duration_seconds": scenario["duration_seconds"],
            "expected_labels": expected_labels,
            "primary_expected_label": primary_expected,
            "detected_labels": detected_labels,
            "events": logical_events,
            "event_message_count": execution["event_message_count"],
            "logical_event_count": execution["logical_event_count"],
            "mqtt": execution["mqtt"],
            "pipeline_summary": execution["pipeline_summary"],
            "demo_outcome": demo_outcome,
            "boundary": (
                "Controlled validation demo. Results are generated by the real ECHO "
                "MVP pipeline and are not a production/field-performance claim."
            ),
        }


    def run_external_audio(
        self,
        path: Path,
        *,
        filename: str,
        media_sha256: str,
        origin: str,
    ) -> dict:
        if origin not in {"user_upload", "microphone_capture"}:
            raise ValueError(f"unsupported demo audio origin: {origin}")
        execution = self._execute_audio(
            path,
            source_id=f"demo:{origin}:{media_sha256[:16]}",
            external_audio=True,
        )
        candidate_events = execution["events"]
        candidate_labels = execution["detected_labels"]
        decision = external_abstention_decision(
            candidate_events=candidate_events,
            candidate_labels=candidate_labels,
            score_diagnostics=execution["score_diagnostics"],
        )
        outcome = (
            "EXTERNAL_AUDIO_NO_TARGET"
            if decision["state"] == "NO_TARGET"
            else "EXTERNAL_AUDIO_UNKNOWN"
        )
        boundary = (
            "External demo audio is analyzed by the real ECHO MVP scorer and temporal "
            "engine, but target publication is blocked by ECHO-DEMO-ABSTENTION-v1. "
            "NO_TARGET means no current target was temporally confirmed. UNKNOWN means "
            "one or more internal target candidates existed, but ECHO abstained because "
            "external-domain acceptance/OOD behavior is not field calibrated. The score "
            "trace is diagnostic only and is not an embedding-distance OOD detector."
        )
        return {
            "scenario_id": None,
            "display_name": filename,
            "partition": None,
            "expected_labels": [],
            "primary_expected_label": None,
            "detected_labels": [],
            "candidate_labels": candidate_labels,
            "events": [],
            "candidate_events": candidate_events,
            "event_message_count": 0,
            "candidate_event_message_count": execution["event_message_count"],
            "logical_event_count": 0,
            "candidate_event_count": execution["logical_event_count"],
            "mqtt": execution["mqtt"],
            "pipeline_summary": execution["pipeline_summary"],
            "score_diagnostics": execution["score_diagnostics"],
            "external_audio_policy": execution["external_audio_policy"],
            "decision_layer": decision,
            "demo_outcome": outcome,
            "audio_origin": origin,
            "uploaded_media_sha256": media_sha256,
            "boundary": boundary,
        }

    def run_uploaded_wav(self, path: Path, *, filename: str, media_sha256: str) -> dict:
        return self.run_external_audio(
            path,
            filename=filename,
            media_sha256=media_sha256,
            origin="user_upload",
        )



class Handler(BaseHTTPRequestHandler):
    app: DemoApplication
    static_dir: Path

    def log_message(self, fmt: str, *args) -> None:
        print("[demo]", fmt % args, flush=True)

    def send_json(self, payload, status=HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def send_file(self, path: Path, content_type: str) -> None:
        raw = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            return self.send_file(self.static_dir / "index.html", "text/html; charset=utf-8")
        if parsed.path == "/api/status":
            return self.send_json(self.app.status())
        if parsed.path == "/api/catalog":
            return self.send_json({"scenarios": self.app.catalog()})
        if parsed.path.startswith("/audio/"):
            scenario_id = parsed.path[len("/audio/") :]
            scenario = self.app.by_id.get(scenario_id)
            if scenario is None:
                return self.send_json({"error": "unknown scenario"}, HTTPStatus.NOT_FOUND)
            return self.send_file(scenario["wav"], "audio/wav")
        return self.send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/run":
            try:
                length = int(self.headers.get("Content-Length") or "0")
                payload = json.loads(self.rfile.read(length) or b"{}")
                scenario_id = str(payload.get("scenario_id") or "")
                if not scenario_id:
                    return self.send_json(
                        {"error": "scenario_id is required"},
                        HTTPStatus.BAD_REQUEST,
                    )
                result = self.app.run(scenario_id)
                return self.send_json(result)
            except KeyError:
                return self.send_json(
                    {"error": "unknown scenario"},
                    HTTPStatus.NOT_FOUND,
                )
            except Exception as exc:
                return self.send_json(
                    {"error": type(exc).__name__, "detail": str(exc)},
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )

        if parsed.path == "/api/recording-run":
            temp_path = None
            try:
                length = int(self.headers.get("Content-Length") or "0")
                if length <= 0:
                    return self.send_json(
                        {"error": "empty recording"},
                        HTTPStatus.BAD_REQUEST,
                    )
                if length > MAX_UPLOAD_BYTES:
                    return self.send_json(
                        {
                            "error": "recording too large",
                            "max_upload_bytes": MAX_UPLOAD_BYTES,
                        },
                        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    )

                content_type = (
                    self.headers.get("Content-Type") or ""
                ).split(";", 1)[0].strip().lower()
                format_by_type = {
                    "audio/webm": (".webm", b"\x1aE\xdf\xa3"),
                    "video/webm": (".webm", b"\x1aE\xdf\xa3"),
                    "audio/ogg": (".ogg", b"OggS"),
                    "application/ogg": (".ogg", b"OggS"),
                    "audio/wav": (".wav", None),
                    "audio/x-wav": (".wav", None),
                }
                if content_type not in format_by_type:
                    return self.send_json(
                        {
                            "error": "unsupported recording format",
                            "content_type": content_type,
                        },
                        HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                    )

                raw = self.rfile.read(length)
                if len(raw) != length:
                    return self.send_json(
                        {"error": "incomplete recording"},
                        HTTPStatus.BAD_REQUEST,
                    )

                suffix, magic = format_by_type[content_type]
                if suffix == ".wav":
                    valid = (
                        len(raw) >= 12
                        and raw[:4] in (b"RIFF", b"RF64")
                        and raw[8:12] == b"WAVE"
                    )
                else:
                    valid = len(raw) >= len(magic) and raw[: len(magic)] == magic
                if not valid:
                    return self.send_json(
                        {"error": "recording container signature is invalid"},
                        HTTPStatus.BAD_REQUEST,
                    )

                media_sha256 = hashlib.sha256(raw).hexdigest()
                filename = Path(
                    self.headers.get("X-Filename")
                    or f"echo-ambient-recording{suffix}"
                ).name
                with tempfile.NamedTemporaryFile(
                    prefix="echo-demo-recording-",
                    suffix=suffix,
                    delete=False,
                ) as handle:
                    handle.write(raw)
                    temp_path = Path(handle.name)

                result = self.app.run_external_audio(
                    temp_path,
                    filename=filename,
                    media_sha256=media_sha256,
                    origin="microphone_capture",
                )
                return self.send_json(result)
            except Exception as exc:
                return self.send_json(
                    {"error": type(exc).__name__, "detail": str(exc)},
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            finally:
                if temp_path is not None:
                    temp_path.unlink(missing_ok=True)

        if parsed.path == "/api/upload-run":
            temp_path = None
            try:
                filename = Path(
                    self.headers.get("X-Filename") or "user-audio.wav"
                ).name
                if Path(filename).suffix.lower() != ".wav":
                    return self.send_json(
                        {"error": "only .wav files are accepted"},
                        HTTPStatus.BAD_REQUEST,
                    )
                length = int(self.headers.get("Content-Length") or "0")
                if length <= 0:
                    return self.send_json(
                        {"error": "empty upload"},
                        HTTPStatus.BAD_REQUEST,
                    )
                if length > MAX_UPLOAD_BYTES:
                    return self.send_json(
                        {
                            "error": "file too large",
                            "max_upload_bytes": MAX_UPLOAD_BYTES,
                        },
                        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    )
                raw = self.rfile.read(length)
                if len(raw) != length:
                    return self.send_json(
                        {"error": "incomplete upload"},
                        HTTPStatus.BAD_REQUEST,
                    )
                if not (
                    len(raw) >= 12
                    and raw[:4] in (b"RIFF", b"RF64")
                    and raw[8:12] == b"WAVE"
                ):
                    return self.send_json(
                        {"error": "file is not a valid WAV container"},
                        HTTPStatus.BAD_REQUEST,
                    )

                media_sha256 = hashlib.sha256(raw).hexdigest()
                with tempfile.NamedTemporaryFile(
                    prefix="echo-demo-",
                    suffix=".wav",
                    delete=False,
                ) as handle:
                    handle.write(raw)
                    temp_path = Path(handle.name)

                result = self.app.run_uploaded_wav(
                    temp_path,
                    filename=filename,
                    media_sha256=media_sha256,
                )
                return self.send_json(result)
            except Exception as exc:
                return self.send_json(
                    {"error": type(exc).__name__, "detail": str(exc)},
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            finally:
                if temp_path is not None:
                    temp_path.unlink(missing_ok=True)

        return self.send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8088)
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=ROOT / "artifacts/mvp-temporal/fixtures.json",
    )
    parser.add_argument(
        "--selection",
        type=Path,
        default=ROOT / "artifacts/mvp-benchmark/selection.json",
    )
    parser.add_argument(
        "--event-config",
        type=Path,
        default=ROOT / "artifacts/mvp-temporal/temporal-event-config.json",
    )
    parser.add_argument(
        "--panns-checkpoint",
        type=Path,
        default=ROOT / "artifacts/models/panns/Cnn14_mAP=0.431.pth",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--mqtt-host", default="broker")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--mqtt-topic", default="echo/events")
    args = parser.parse_args()

    app = DemoApplication(args)
    Handler.app = app
    Handler.static_dir = ROOT / "demo"
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(
        json.dumps(
            {
                "status": "READY",
                "url": f"http://{args.host}:{args.port}",
                "mode": app.status()["mode"],
                "model": app.benchmark,
                "threshold_version": app.threshold_version,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    try:
        server.serve_forever()
    finally:
        app.close()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
