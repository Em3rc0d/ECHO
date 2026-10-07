#!/usr/bin/env python3
"""Run the Docker-first ECHO MVP controlled temporal calibration pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--media-index",
        type=Path,
        default=ROOT / "artifacts/mvp-media/mvp-media-index.json",
    )
    parser.add_argument(
        "--selection",
        type=Path,
        default=ROOT / "artifacts/mvp-benchmark/selection.json",
    )
    parser.add_argument(
        "--panns-checkpoint",
        type=Path,
        default=ROOT / "artifacts/models/panns/Cnn14_mAP=0.431.pth",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "artifacts/mvp-temporal",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--window-seconds", type=float, default=6.0)
    parser.add_argument("--hop-seconds", type=float, default=1.0)
    parser.add_argument("--force-rescore", action="store_true")
    args = parser.parse_args()

    python = sys.executable
    fixtures = args.output_dir / "fixtures.json"
    score_summary = args.output_dir / "score-summary.json"

    run(
        [
            python,
            "scripts/mvp/prepare_temporal_calibration.py",
            "--media-index",
            str(args.media_index),
            "--output-dir",
            str(args.output_dir),
        ]
    )

    score_command = [
        python,
        "scripts/mvp/score_temporal_calibration.py",
        "--fixtures",
        str(fixtures),
        "--selection",
        str(args.selection),
        "--panns-checkpoint",
        str(args.panns_checkpoint),
        "--output-dir",
        str(args.output_dir / "scores"),
        "--device",
        args.device,
        "--window-seconds",
        str(args.window_seconds),
        "--hop-seconds",
        str(args.hop_seconds),
    ]
    if args.force_rescore:
        score_command.append("--force")
    run(score_command)

    run(
        [
            python,
            "scripts/mvp/select_temporal_policy.py",
            "--fixtures",
            str(fixtures),
            "--score-summary",
            str(score_summary),
            "--selection",
            str(args.selection),
            "--output-dir",
            str(args.output_dir),
        ]
    )

    report_path = args.output_dir / "calibration-report.json"
    config_path = args.output_dir / "temporal-event-config.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "status": report["status"],
                "config": str(config_path),
                "report": str(report_path),
                "macro": report["macro"],
                "warnings": report.get("warnings") or [],
                "boundary": report["boundary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
