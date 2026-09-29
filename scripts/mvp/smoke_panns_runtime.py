#!/usr/bin/env python3
"""Fast runtime smoke for the pinned PANNs Cnn14 stack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echo.modeling.backbones import PannsCnn14EmbeddingBackbone


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    if not args.checkpoint.is_file():
        raise SystemExit(f"PANNs checkpoint missing: {args.checkpoint}")

    try:
        import numpy as np
    except ImportError as exc:
        raise SystemExit("PANNs runtime smoke requires numpy") from exc

    backbone = PannsCnn14EmbeddingBackbone(
        checkpoint_path=str(args.checkpoint),
        device=args.device,
    )
    waveform = np.zeros(backbone.sample_rate_hz * 2, dtype=np.float32)
    embedding = np.asarray(backbone.embed(waveform), dtype=np.float32)

    if embedding.shape != (backbone.embedding_dim,):
        raise RuntimeError(
            f"PANNs embedding shape {embedding.shape} != {(backbone.embedding_dim,)}"
        )
    if not bool(np.isfinite(embedding).all()):
        raise RuntimeError("PANNs embedding contains non-finite values")

    print(
        json.dumps(
            {
                "schema_version": "echo.panns-runtime-smoke.v1",
                "status": "PASS",
                "device": args.device,
                "sample_rate_hz": backbone.sample_rate_hz,
                "embedding_dim": int(embedding.shape[0]),
                "checkpoint": str(args.checkpoint),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
