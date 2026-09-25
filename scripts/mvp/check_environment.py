#!/usr/bin/env python3
"""Fail-fast environment preflight for the full ECHO-MVP-001 execution path."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

MODULES = {
    "numpy": "numpy",
    "torch": "torch",
    "paho-mqtt": "paho.mqtt.client",
    "tensorflow": "tensorflow",
    "tensorflow-hub": "tensorflow_hub",
    "panns-inference": "panns_inference",
}


def version_for(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--storage-root",
        type=Path,
        default=ROOT / "artifacts",
    )
    parser.add_argument(
        "--min-free-gib",
        type=float,
        default=2.0,
        help="Fail below this free-space floor before large corpus/model downloads.",
    )
    args = parser.parse_args()

    gaps: list[str] = []
    checks: dict[str, object] = {}

    if sys.version_info < (3, 10):
        gaps.append(f"PYTHON_TOO_OLD:{sys.version.split()[0]}")
    checks["python"] = sys.version.split()[0]

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        gaps.append("FFMPEG_NOT_FOUND")
        checks["ffmpeg"] = None
    else:
        probe = subprocess.run(
            [ffmpeg, "-version"],
            check=False,
            capture_output=True,
            text=True,
        )
        first_line = (probe.stdout or probe.stderr).splitlines()
        checks["ffmpeg"] = first_line[0] if first_line else ffmpeg
        if probe.returncode != 0:
            gaps.append(f"FFMPEG_EXEC_FAILED:{probe.returncode}")

    dependencies = {}
    for distribution, module in MODULES.items():
        found = importlib.util.find_spec(module) is not None
        dependencies[distribution] = {
            "module": module,
            "found": found,
            "version": version_for(distribution),
        }
        if not found:
            gaps.append(f"DEPENDENCY_MISSING:{distribution}")

    storage_root = args.storage_root.resolve()
    storage_root.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage(storage_root)
    free_gib = usage.free / (1024 ** 3)
    checks["storage"] = {
        "root": str(storage_root),
        "free_bytes": usage.free,
        "free_gib": round(free_gib, 3),
        "minimum_free_gib": args.min_free_gib,
    }
    if free_gib < args.min_free_gib:
        gaps.append(
            f"FREE_SPACE_BELOW_FLOOR:{free_gib:.3f}<{args.min_free_gib:.3f}GiB"
        )

    device = args.device.casefold()
    if device.startswith("cuda"):
        if not dependencies["torch"]["found"]:
            gaps.append("CUDA_REQUESTED_WITHOUT_TORCH")
        else:
            import torch

            checks["cuda"] = {
                "available": bool(torch.cuda.is_available()),
                "device_count": int(torch.cuda.device_count()),
            }
            if not torch.cuda.is_available():
                gaps.append("CUDA_REQUESTED_BUT_UNAVAILABLE")

    payload = {
        "schema_version": "echo.mvp-environment-preflight.v1",
        "profile_id": "ECHO-MVP-001",
        "status": "PASS" if not gaps else "FAIL",
        "device": args.device,
        "checks": checks,
        "dependencies": dependencies,
        "gap_codes": gaps,
        "install_hint": 'python -m pip install -e ".[mvp-full]"',
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not gaps else 3


if __name__ == "__main__":
    raise SystemExit(main())
