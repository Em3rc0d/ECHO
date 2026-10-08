#!/usr/bin/env python3
"""ECHO professor demo adapter.

This adapter intentionally does not implement classification logic. It loads the
selected ECHO MVP model, the current temporal Event Engine configuration and
routes real controlled-validation WAV fixtures through EchoReplayPipeline. The
same echo.event.v1 payloads are published over MQTT QoS 1.

The demo is a presentation surface, not an alternate inference path.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
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

    def run(self, scenario_id: str) -> dict:
        if scenario_id not in self.by_id:
            raise KeyError(scenario_id)
        scenario = self.by_id[scenario_id]
        collector = CollectingPublisher()
        engine = TemporalEventEngine(
            thresholds=self.thresholds,
            threshold_version=self.threshold_version,
        )
        pipeline = EchoReplayPipeline(
            scorer=self.scorer,
            event_engine=engine,
            publishers=[collector, self.mqtt],
        )
        with self.lock:
            summary = pipeline.run_file(
                scenario["wav"],
                source_id=f"demo:{scenario_id}",
                site_id="ECHO-PROFESSOR-DEMO",
                window_seconds=float(
                    self.config_payload.get("window_seconds") or 6.0
                ),
                hop_seconds=float(
                    self.config_payload.get("hop_seconds") or 1.0
                ),
                pad_final=True,
            )
        logical_events = aggregate_events(collector.events)
        detected_labels = sorted(
            {
                str(row["event_type"])
                for row in logical_events
                if "CONFIRMED" in row["lifecycles"]
            }
        )
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
            "event_message_count": len(collector.events),
            "logical_event_count": len(logical_events),
            "mqtt": {
                "published": True,
                "topic": self.args.mqtt_topic,
                "qos": 1,
            },
            "pipeline_summary": summary,
            "demo_outcome": demo_outcome,
            "boundary": (
                "Controlled validation demo. Results are generated by the real ECHO "
                "MVP pipeline and are not a production/field-performance claim."
            ),
        }


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
        if parsed.path != "/api/run":
            return self.send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
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
            return self.send_json({"error": "unknown scenario"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            return self.send_json(
                {"error": type(exc).__name__, "detail": str(exc)},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )


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
