#!/usr/bin/env python3
"""Run the first ECHO MVP replay E2E with a trained benchmark checkpoint."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echo.modeling.inference import CompactCnnScorer, EmbeddingHeadScorer
from echo.runtime.event_engine import TemporalEventEngine, ThresholdConfig
from echo.runtime.pipeline import EchoReplayPipeline
from echo.runtime.publishers import JsonlEventPublisher, MqttEventPublisher


def load_event_config(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = str(payload.get("threshold_version") or "")
    labels = payload.get("labels")
    if not version or not isinstance(labels, dict) or not labels:
        raise ValueError("event config requires threshold_version and labels")
    thresholds = {}
    for label, row in labels.items():
        if not isinstance(row, dict):
            raise ValueError(f"event config label {label}: expected object")
        thresholds[str(label)] = ThresholdConfig(
            on_threshold=float(row["on_threshold"]),
            off_threshold=float(row["off_threshold"]),
            confirm_windows=int(row["confirm_windows"]),
            release_windows=int(row["release_windows"]),
            cooldown_seconds=float(row.get("cooldown_seconds", 0.0)),
        )
    return version, thresholds


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=("yamnet", "panns", "compact"), required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--event-config", type=Path, required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--site-id", required=True)
    parser.add_argument("--window-seconds", type=float, required=True)
    parser.add_argument("--hop-seconds", type=float, required=True)
    parser.add_argument(
        "--events-jsonl",
        type=Path,
        default=ROOT / "artifacts/mvp-replay/events.jsonl",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--yamnet-handle", default="https://tfhub.dev/google/yamnet/1")
    parser.add_argument("--panns-checkpoint", default=None)
    parser.add_argument("--start-utc", default=None)
    parser.add_argument("--mqtt-host", default=None)
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--mqtt-topic", default=None)
    parser.add_argument("--mqtt-client-id", default="echo-mvp")
    parser.add_argument("--mqtt-username", default=None)
    parser.add_argument("--mqtt-password-env", default=None)
    args = parser.parse_args()

    if args.model == "compact":
        scorer = CompactCnnScorer(checkpoint=args.checkpoint, device=args.device)
    else:
        scorer = EmbeddingHeadScorer(
            checkpoint=args.checkpoint,
            backbone=args.model,
            device=args.device,
            yamnet_handle=args.yamnet_handle,
            panns_checkpoint=args.panns_checkpoint,
        )

    threshold_version, thresholds = load_event_config(args.event_config)
    engine = TemporalEventEngine(
        thresholds=thresholds,
        threshold_version=threshold_version,
    )

    publishers = [JsonlEventPublisher(args.events_jsonl)]
    mqtt = None
    if args.mqtt_host is not None:
        if not args.mqtt_topic:
            raise SystemExit("--mqtt-topic is required when --mqtt-host is used")
        password = (
            os.environ.get(args.mqtt_password_env)
            if args.mqtt_password_env
            else None
        )
        mqtt = MqttEventPublisher(
            host=args.mqtt_host,
            port=args.mqtt_port,
            topic=args.mqtt_topic,
            client_id=args.mqtt_client_id,
            username=args.mqtt_username,
            password=password,
        )
        publishers.append(mqtt)

    try:
        pipeline = EchoReplayPipeline(
            scorer=scorer,
            event_engine=engine,
            publishers=publishers,
        )
        start = datetime.fromisoformat(args.start_utc) if args.start_utc else None
        summary = pipeline.run_file(
            args.audio,
            source_id=args.source_id,
            site_id=args.site_id,
            window_seconds=args.window_seconds,
            hop_seconds=args.hop_seconds,
            start_utc=start,
        )
    finally:
        if mqtt is not None:
            mqtt.close()

    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
