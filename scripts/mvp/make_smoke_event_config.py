#!/usr/bin/env python3
"""Create a transparent smoke-only Event Engine config from validation thresholds.

This deliberately does NOT claim temporal calibration. The benchmark-selected
per-window validation thresholds become on/off thresholds and confirmation is a
single window so the first E2E smoke tests wiring, not a hidden temporal policy.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

TARGETS = ("GLASS_SHATTER", "SIREN", "VEHICLE_HORN")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--selection",
        type=Path,
        default=Path("artifacts/mvp-benchmark/selection.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/mvp-benchmark/smoke-event-config.json"),
    )
    args = parser.parse_args()

    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    winner = selection.get("winner") or {}
    thresholds = winner.get("validation_thresholds") or {}
    missing = [target for target in TARGETS if target not in thresholds]
    if missing:
        raise SystemExit(f"winner selection missing validation thresholds: {missing}")

    labels = {}
    for target in TARGETS:
        value = float(thresholds[target])
        if not 0.0 <= value <= 1.0:
            raise SystemExit(f"invalid validation threshold for {target}: {value}")
        labels[target] = {
            "on_threshold": value,
            "off_threshold": value,
            "confirm_windows": 1,
            "release_windows": 1,
            "cooldown_seconds": 0.0,
        }

    payload = {
        "schema_version": "echo.event-threshold-config.v1",
        "threshold_version": "ECHO-MVP-001-SMOKE-VALIDATION-THRESHOLDS-v1",
        "status": "SMOKE_ONLY_NOT_TEMPORALLY_CALIBRATED",
        "profile_id": "ECHO-MVP-001",
        "model_benchmark": winner.get("benchmark"),
        "selection_source": str(args.selection),
        "labels": labels,
        "boundary": (
            "Single-window smoke wiring only. Threshold values were selected on "
            "benchmark validation data; confirmation/release/cooldown are not "
            "field or long-stream calibrated and must not be promoted as release policy."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
