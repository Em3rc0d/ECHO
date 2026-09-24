#!/usr/bin/env python3
"""Run ECHO-MVP-001 Benchmarks A/B/C and select the provisional winner."""

from __future__ import annotations

import argparse
import json
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
    parser.add_argument("--media-index", type=Path, required=True)
    parser.add_argument("--panns-checkpoint", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "MK1/mining-site/materialization/mvp-benchmark-manifest.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "artifacts/mvp-benchmark",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--epochs-head", type=int, default=80)
    parser.add_argument("--epochs-cnn", type=int, default=40)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--yamnet-handle", default="https://tfhub.dev/google/yamnet/1")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required on PATH")
    if not args.panns_checkpoint.is_file():
        raise SystemExit(f"PANNs checkpoint not found: {args.panns_checkpoint}")

    media = json.loads(args.media_index.read_text(encoding="utf-8"))
    if media.get("status") != "COMPLETE":
        raise SystemExit(
            f"MVP media index must be COMPLETE, got {media.get('status')!r}"
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    python = sys.executable

    run(
        [
            python,
            "scripts/mvp/run_embedding_benchmark.py",
            "--backbone",
            "yamnet",
            "--manifest",
            str(args.manifest),
            "--media-index",
            str(args.media_index),
            "--output-dir",
            str(args.output_dir),
            "--device",
            args.device,
            "--epochs",
            str(args.epochs_head),
            "--seed",
            str(args.seed),
            "--yamnet-handle",
            args.yamnet_handle,
        ]
    )
    run(
        [
            python,
            "scripts/mvp/run_embedding_benchmark.py",
            "--backbone",
            "panns",
            "--manifest",
            str(args.manifest),
            "--media-index",
            str(args.media_index),
            "--output-dir",
            str(args.output_dir),
            "--device",
            args.device,
            "--epochs",
            str(args.epochs_head),
            "--seed",
            str(args.seed),
            "--panns-checkpoint",
            str(args.panns_checkpoint),
        ]
    )
    run(
        [
            python,
            "scripts/mvp/run_compact_cnn_benchmark.py",
            "--manifest",
            str(args.manifest),
            "--media-index",
            str(args.media_index),
            "--output-dir",
            str(args.output_dir / "compact-cnn"),
            "--device",
            args.device,
            "--epochs",
            str(args.epochs_cnn),
            "--seed",
            str(args.seed),
        ]
    )

    selection = args.output_dir / "selection.json"
    run(
        [
            python,
            "scripts/mvp/compare_benchmarks.py",
            str(args.output_dir / "yamnet" / "result.json"),
            str(args.output_dir / "panns" / "result.json"),
            str(args.output_dir / "compact-cnn" / "result.json"),
            "--output",
            str(selection),
        ]
    )

    payload = json.loads(selection.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "winner": payload["winner"]["benchmark"],
                "selection": str(selection),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
