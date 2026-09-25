#!/usr/bin/env python3
"""One resumable command for the first ECHO-MVP-001 model/replay vertical."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--media-root",
        type=Path,
        default=ROOT / "artifacts/mvp-media",
    )
    parser.add_argument(
        "--benchmark-root",
        type=Path,
        default=ROOT / "artifacts/mvp-benchmark",
    )
    parser.add_argument(
        "--panns-checkpoint",
        type=Path,
        default=ROOT / "artifacts/models/panns/Cnn14_mAP=0.431.pth",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--direct-workers", type=int, default=6)
    parser.add_argument("--skip-materialize", action="store_true")
    parser.add_argument("--skip-checkpoint-fetch", action="store_true")
    parser.add_argument("--skip-benchmarks", action="store_true")
    parser.add_argument("--skip-smoke", action="store_true")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required on PATH")

    python = sys.executable
    run([python, "scripts/mvp/smoke_core_synthetic.py"])
    run([python, "scripts/mvp/check_frozen_mvp_snapshot.py"])

    media_index = args.media_root / "mvp-media-index.json"
    selection = args.benchmark_root / "selection.json"
    smoke_config = args.benchmark_root / "smoke-event-config.json"

    if not args.skip_materialize:
        run(
            [
                python,
                "scripts/mvp/materialize_mvp_media.py",
                "--root",
                str(args.media_root),
                "--direct-workers",
                str(args.direct_workers),
            ]
        )
    elif not media_index.is_file():
        raise SystemExit(f"--skip-materialize but media index missing: {media_index}")

    if not args.skip_checkpoint_fetch:
        run(
            [
                python,
                "scripts/mvp/fetch_panns_checkpoint.py",
                "--output",
                str(args.panns_checkpoint),
            ]
        )
    elif not args.panns_checkpoint.is_file():
        raise SystemExit(
            f"--skip-checkpoint-fetch but PANNs checkpoint missing: {args.panns_checkpoint}"
        )

    if not args.skip_benchmarks:
        run(
            [
                python,
                "scripts/mvp/run_all_benchmarks.py",
                "--media-index",
                str(media_index),
                "--panns-checkpoint",
                str(args.panns_checkpoint),
                "--output-dir",
                str(args.benchmark_root),
                "--device",
                args.device,
            ]
        )
    elif not selection.is_file():
        raise SystemExit(f"--skip-benchmarks but selection missing: {selection}")

    run(
        [
            python,
            "scripts/mvp/make_smoke_event_config.py",
            "--selection",
            str(selection),
            "--output",
            str(smoke_config),
        ]
    )

    if not args.skip_smoke:
        run(
            [
                python,
                "scripts/mvp/smoke_selected_model.py",
                "--selection",
                str(selection),
                "--event-config",
                str(smoke_config),
                "--media-index",
                str(media_index),
                "--panns-checkpoint",
                str(args.panns_checkpoint),
                "--device",
                args.device,
            ]
        )

    print("ECHO-MVP-001 execution path complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
