#!/usr/bin/env python3
"""Run Benchmark A (YAMNet) or B (PANNs/Cnn14) for ECHO-MVP-001."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echo.modeling.audio import decode_audio_f32_mono
from echo.modeling.backbones import (
    PannsCnn14EmbeddingBackbone,
    YAMNetEmbeddingBackbone,
)
from echo.modeling.embedding_head import HeadTrainingConfig, train_embedding_head
from echo.modeling.manifest import load_benchmark_manifest


def load_media_index(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "COMPLETE":
        raise SystemExit(
            f"media index is not COMPLETE: missing={payload.get('missing_sha256_count')}"
        )
    by_sha = payload.get("by_sha256")
    if not isinstance(by_sha, dict):
        raise ValueError("media index missing by_sha256")
    return {str(k): str(v) for k, v in by_sha.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backbone", choices=("yamnet", "panns"), required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "MK1/mining-site/materialization/mvp-benchmark-manifest.jsonl",
    )
    parser.add_argument("--media-index", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "artifacts/mvp-benchmark",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--yamnet-handle", default="https://tfhub.dev/google/yamnet/1")
    parser.add_argument("--panns-checkpoint", default=None)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--max-assets", type=int, default=None)
    args = parser.parse_args()

    try:
        import numpy as np
        import torch
    except ImportError as exc:
        raise SystemExit("install ECHO with the 'mvp' extra") from exc

    rows = load_benchmark_manifest(args.manifest)
    if args.max_assets is not None:
        rows = rows[: args.max_assets]
    media_index = load_media_index(args.media_index)

    if args.backbone == "yamnet":
        backbone = YAMNetEmbeddingBackbone(model_handle=args.yamnet_handle)
    else:
        backbone = PannsCnn14EmbeddingBackbone(
            checkpoint_path=args.panns_checkpoint,
            device=args.device,
        )

    output_dir = args.output_dir / args.backbone
    feature_dir = output_dir / "features"
    feature_dir.mkdir(parents=True, exist_ok=True)

    vectors = []
    for index, row in enumerate(rows, 1):
        media_path = media_index.get(row.media_sha256)
        if not media_path:
            raise SystemExit(
                f"media index missing governed bytes for {row.asset_id} "
                f"({row.media_sha256})"
            )
        cache_path = feature_dir / f"{row.media_sha256}.npy"
        if cache_path.is_file():
            vector = np.load(cache_path)
        else:
            waveform = decode_audio_f32_mono(
                media_path,
                sample_rate_hz=backbone.sample_rate_hz,
            )
            vector = np.asarray(backbone.embed(waveform), dtype=np.float32)
            np.save(cache_path, vector)
        if vector.shape != (backbone.embedding_dim,):
            raise RuntimeError(
                f"{row.asset_id}: embedding shape {vector.shape} "
                f"!= {(backbone.embedding_dim,)}"
            )
        vectors.append(vector)
        if index % 50 == 0 or index == len(rows):
            print(f"features {index}/{len(rows)}", flush=True)

    features = np.stack(vectors, axis=0)
    model, report = train_embedding_head(
        features=features,
        rows=rows,
        input_dim=backbone.embedding_dim,
        config=HeadTrainingConfig(
            epochs=args.epochs,
            batch_size=args.batch_size,
            seed=args.seed,
        ),
        device=args.device,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = output_dir / "echo-head.pt"
    torch.save(
        {
            "backbone": backbone.name,
            "input_dim": backbone.embedding_dim,
            "targets": ["GLASS_SHATTER", "SIREN", "VEHICLE_HORN"],
            "state_dict": model.state_dict(),
            "validation_thresholds": report["validation_thresholds"],
            "seed": args.seed,
        },
        checkpoint,
    )

    result = {
        "schema_version": "echo.mvp-benchmark-result.v1",
        "profile_id": "ECHO-MVP-001",
        "benchmark": backbone.name,
        "manifest": str(args.manifest),
        "media_index": str(args.media_index),
        "asset_count": len(rows),
        "sample_rate_hz": backbone.sample_rate_hz,
        "embedding_dim": backbone.embedding_dim,
        "checkpoint": str(checkpoint),
        **report,
    }
    result_path = output_dir / "result.json"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"result": str(result_path), "test": result["test"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
