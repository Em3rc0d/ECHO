#!/usr/bin/env python3
"""Smoke the selected ECHO MVP model through replay -> Event Engine.

This is a wiring/demo gate, not model evaluation: benchmark metrics were already
computed on the full frozen test split. The smoke passes when at least one
frozen positive test clip per MVP target produces a CONFIRMED event.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echo.modeling.inference import CompactCnnScorer, EmbeddingHeadScorer
from echo.modeling.manifest import MVP_TARGETS, load_benchmark_manifest
from echo.runtime.event_engine import TemporalEventEngine, ThresholdConfig
from echo.runtime.pipeline import EchoReplayPipeline
from echo.runtime.publishers import JsonlEventPublisher


class CollectingPublisher:
    def __init__(self):
        self.events: list[dict] = []

    def publish(self, event):
        self.events.append(dict(event))


def load_thresholds(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    labels = payload.get("labels") or {}
    return str(payload["threshold_version"]), {
        str(label): ThresholdConfig(
            on_threshold=float(row["on_threshold"]),
            off_threshold=float(row["off_threshold"]),
            confirm_windows=int(row["confirm_windows"]),
            release_windows=int(row["release_windows"]),
            cooldown_seconds=float(row.get("cooldown_seconds", 0.0)),
        )
        for label, row in labels.items()
    }


def resolve_checkpoint(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    if not path.is_file():
        raise SystemExit(f"winner checkpoint not found: {path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--selection",
        type=Path,
        default=ROOT / "artifacts/mvp-benchmark/selection.json",
    )
    parser.add_argument(
        "--event-config",
        type=Path,
        default=ROOT / "artifacts/mvp-benchmark/smoke-event-config.json",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "MK1/mining-site/materialization/mvp-benchmark-manifest.jsonl",
    )
    parser.add_argument("--media-index", type=Path, required=True)
    parser.add_argument("--panns-checkpoint", type=Path, default=None)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--clips-per-class", type=int, default=5)
    parser.add_argument("--window-seconds", type=float, default=6.0)
    parser.add_argument("--hop-seconds", type=float, default=3.0)
    parser.add_argument(
        "--events-jsonl",
        type=Path,
        default=ROOT / "artifacts/mvp-smoke/events.jsonl",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "artifacts/mvp-smoke/report.json",
    )
    args = parser.parse_args()

    if args.clips_per_class < 1:
        raise SystemExit("--clips-per-class must be >= 1")

    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    winner = selection["winner"]
    benchmark = str(winner["benchmark"])
    checkpoint = resolve_checkpoint(str(winner["checkpoint"]))

    if benchmark == "YAMNET_EMBEDDINGS_HEAD":
        scorer = EmbeddingHeadScorer(
            checkpoint=checkpoint,
            backbone="yamnet",
            device=args.device,
        )
    elif benchmark == "PANNS_CNN14_HEAD":
        if args.panns_checkpoint is None:
            raise SystemExit("--panns-checkpoint required when PANNs wins")
        scorer = EmbeddingHeadScorer(
            checkpoint=checkpoint,
            backbone="panns",
            device=args.device,
            panns_checkpoint=str(args.panns_checkpoint),
        )
    elif benchmark == "COMPACT_LOGMEL_CNN":
        scorer = CompactCnnScorer(checkpoint=checkpoint, device=args.device)
    else:
        raise SystemExit(f"unsupported winner benchmark: {benchmark}")

    media_payload = json.loads(args.media_index.read_text(encoding="utf-8"))
    if media_payload.get("status") != "COMPLETE":
        raise SystemExit("media index must be COMPLETE")
    by_sha = {
        str(key): str(value)
        for key, value in (media_payload.get("by_sha256") or {}).items()
    }

    rows = load_benchmark_manifest(args.manifest)
    version, thresholds = load_thresholds(args.event_config)

    candidates = {
        target: [
            row
            for row in rows
            if row.split == "test" and target in row.positive_labels
        ][: args.clips_per_class]
        for target in MVP_TARGETS
    }
    for target, selected in candidates.items():
        if not selected:
            raise SystemExit(f"no positive test smoke candidates for {target}")

    args.events_jsonl.parent.mkdir(parents=True, exist_ok=True)
    args.events_jsonl.unlink(missing_ok=True)

    report_classes = {}
    for target in MVP_TARGETS:
        attempted = 0
        confirmed = 0
        rows_report = []
        for row in candidates[target]:
            path = by_sha.get(row.media_sha256)
            if not path:
                raise SystemExit(f"media index missing {row.media_sha256}")

            collector = CollectingPublisher()
            file_publisher = JsonlEventPublisher(args.events_jsonl)
            engine = TemporalEventEngine(
                thresholds=thresholds,
                threshold_version=version,
            )
            pipeline = EchoReplayPipeline(
                scorer=scorer,
                event_engine=engine,
                publishers=[collector, file_publisher],
            )
            summary = pipeline.run_file(
                path,
                source_id=f"mvp-smoke:{target.lower()}",
                site_id="ECHO-MVP-SMOKE",
                window_seconds=args.window_seconds,
                hop_seconds=args.hop_seconds,
                pad_final=True,
            )
            matching = [
                event
                for event in collector.events
                if event.get("event_type") == target
                and (event.get("provenance") or {}).get("lifecycle") == "CONFIRMED"
            ]
            attempted += 1
            if matching:
                confirmed += 1
            rows_report.append(
                {
                    "asset_id": row.asset_id,
                    "media_sha256": row.media_sha256,
                    "window_count": summary["window_count"],
                    "event_message_count": summary["event_message_count"],
                    "target_confirmed": bool(matching),
                }
            )

        report_classes[target] = {
            "clips_attempted": attempted,
            "clips_with_target_confirmed": confirmed,
            "status": "PASS" if confirmed > 0 else "FAIL",
            "clips": rows_report,
        }

    passed = all(row["status"] == "PASS" for row in report_classes.values())
    payload = {
        "schema_version": "echo.mvp-e2e-smoke.v1",
        "profile_id": "ECHO-MVP-001",
        "status": "PASS" if passed else "FAIL",
        "scope": (
            "Model -> replay windows -> RawInference -> TemporalEventEngine -> "
            "echo.event.v1 JSONL. Smoke-only thresholds; not temporal calibration."
        ),
        "winner": benchmark,
        "checkpoint": str(checkpoint),
        "event_config": str(args.event_config),
        "classes": report_classes,
        "events_jsonl": str(args.events_jsonl),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "report": str(args.report)}, sort_keys=True))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
