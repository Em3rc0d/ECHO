#!/usr/bin/env python3
"""Run Benchmark C: compact ECHO log-mel CNN on ECHO-MVP-001."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echo.modeling.audio import decode_audio_f32_mono
from echo.modeling.compact_cnn import build_compact_cnn
from echo.modeling.embedding_head import (
    evaluate_multilabel,
    supervision_arrays,
    tune_multilabel_thresholds,
)
from echo.modeling.manifest import MVP_TARGETS, load_benchmark_manifest


def load_media_index(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "COMPLETE":
        raise SystemExit(
            f"media index is not COMPLETE: missing={payload.get('missing_sha256_count')}"
        )
    return {str(k): str(v) for k, v in (payload.get("by_sha256") or {}).items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "MK1/mining-site/materialization/mvp-benchmark-manifest.jsonl",
    )
    parser.add_argument("--media-index", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "artifacts/mvp-benchmark/compact-cnn",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--clip-seconds", type=float, default=6.0)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--seed", type=int, default=1337)
    args = parser.parse_args()

    try:
        import numpy as np
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, Dataset
    except ImportError as exc:
        raise SystemExit("install ECHO with the 'mvp' extra") from exc

    rows = load_benchmark_manifest(args.manifest)
    media = load_media_index(args.media_index)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    target_samples = int(round(args.sample_rate * args.clip_seconds))
    if target_samples <= 0:
        raise SystemExit("clip length must be positive")

    waveform_identity = f"sr{args.sample_rate}-samples{target_samples}"
    waveform_dir = args.output_dir / "waveforms" / waveform_identity
    waveform_dir.mkdir(parents=True, exist_ok=True)

    for index, row in enumerate(rows, 1):
        path = media.get(row.media_sha256)
        if not path:
            raise SystemExit(f"missing media for {row.asset_id}")
        cache = waveform_dir / f"{row.media_sha256}.npy"
        if not cache.is_file():
            waveform = np.asarray(
                decode_audio_f32_mono(path, sample_rate_hz=args.sample_rate),
                dtype=np.float32,
            )
            if waveform.size >= target_samples:
                start = (waveform.size - target_samples) // 2
                waveform = waveform[start : start + target_samples]
            else:
                waveform = np.pad(
                    waveform,
                    (0, target_samples - waveform.size),
                    mode="constant",
                )
            np.save(cache, waveform)
        if index % 50 == 0 or index == len(rows):
            print(f"waveforms {index}/{len(rows)}", flush=True)

    y, mask = supervision_arrays(rows)

    class AudioDataset(Dataset):
        def __init__(self, indices):
            self.indices = list(indices)

        def __len__(self):
            return len(self.indices)

        def __getitem__(self, offset):
            i = self.indices[offset]
            waveform = np.load(waveform_dir / f"{rows[i].media_sha256}.npy")
            return (
                torch.as_tensor(waveform, dtype=torch.float32),
                torch.as_tensor(y[i], dtype=torch.float32),
                torch.as_tensor(mask[i], dtype=torch.float32),
                i,
            )

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    split_indices = {
        split: np.asarray(
            [i for i, row in enumerate(rows) if row.split == split],
            dtype=np.int64,
        )
        for split in ("train", "validation", "test")
    }

    model = build_compact_cnn(
        num_targets=len(MVP_TARGETS),
        sample_rate_hz=args.sample_rate,
        f_max=args.sample_rate / 2,
    ).to(args.device)

    train_y = y[split_indices["train"]]
    train_mask = mask[split_indices["train"]]
    pos_weights = []
    for j in range(len(MVP_TARGETS)):
        known = train_mask[:, j] > 0.5
        positives = float(train_y[known, j].sum())
        negatives = float(known.sum() - positives)
        pos_weights.append(negatives / positives if positives > 0 else 1.0)

    loss_fn = nn.BCEWithLogitsLoss(
        reduction="none",
        pos_weight=torch.tensor(pos_weights, dtype=torch.float32, device=args.device),
    )
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )

    train_loader = DataLoader(
        AudioDataset(split_indices["train"]),
        batch_size=args.batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(args.seed),
    )

    def predict(indices):
        loader = DataLoader(
            AudioDataset(indices),
            batch_size=args.batch_size,
            shuffle=False,
        )
        all_probs = []
        all_indices = []
        model.eval()
        with torch.no_grad():
            for waveforms, _yb, _mb, batch_indices in loader:
                logits = model(waveforms.to(args.device))
                all_probs.append(torch.sigmoid(logits).cpu())
                all_indices.extend(int(v) for v in batch_indices)
        return torch.cat(all_probs, dim=0).numpy(), np.asarray(all_indices)

    best = {
        "macro_f1": -1.0,
        "epoch": 0,
        "state_dict": None,
        "thresholds": None,
        "validation": None,
    }
    stale = 0

    for epoch in range(1, args.epochs + 1):
        model.train()
        for waveforms, yb, mb, _indices in train_loader:
            waveforms = waveforms.to(args.device)
            yb = yb.to(args.device)
            mb = mb.to(args.device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(waveforms)
            raw = loss_fn(logits, yb)
            loss = (raw * mb).sum() / mb.sum().clamp_min(1.0)
            loss.backward()
            optimizer.step()

        val_probs, val_indices = predict(split_indices["validation"])
        thresholds, val_report = tune_multilabel_thresholds(
            val_probs,
            y[val_indices],
            mask[val_indices],
        )
        if val_report["macro_f1"] > best["macro_f1"] + 1e-12:
            best = {
                "macro_f1": val_report["macro_f1"],
                "epoch": epoch,
                "state_dict": deepcopy(model.state_dict()),
                "thresholds": thresholds,
                "validation": val_report,
            }
            stale = 0
        else:
            stale += 1
            if stale >= args.patience:
                break

    if best["state_dict"] is None:
        raise RuntimeError("compact CNN failed to produce a checkpoint")

    model.load_state_dict(best["state_dict"])
    test_probs, test_indices = predict(split_indices["test"])
    test_report = evaluate_multilabel(
        test_probs,
        y[test_indices],
        mask[test_indices],
        best["thresholds"],
    )

    checkpoint = args.output_dir / "compact-cnn.pt"
    torch.save(
        {
            "benchmark": "COMPACT_LOGMEL_CNN",
            "targets": list(MVP_TARGETS),
            "sample_rate_hz": args.sample_rate,
            "clip_seconds": args.clip_seconds,
            "waveform_cache_identity": waveform_identity,
            "state_dict": model.state_dict(),
            "validation_thresholds": best["thresholds"],
            "seed": args.seed,
        },
        checkpoint,
    )

    result = {
        "schema_version": "echo.mvp-benchmark-result.v1",
        "profile_id": "ECHO-MVP-001",
        "benchmark": "COMPACT_LOGMEL_CNN",
        "asset_count": len(rows),
        "sample_rate_hz": args.sample_rate,
        "clip_seconds": args.clip_seconds,
        "waveform_cache_identity": waveform_identity,
        "selected_epoch": best["epoch"],
        "validation_thresholds": best["thresholds"],
        "validation": best["validation"],
        "test": test_report,
        "training": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "weight_decay": args.weight_decay,
            "patience": args.patience,
            "seed": args.seed,
            "positive_weights": {
                target: float(pos_weights[j])
                for j, target in enumerate(MVP_TARGETS)
            },
        },
        "checkpoint": str(checkpoint),
    }
    result_path = args.output_dir / "result.json"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"result": str(result_path), "test": test_report}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
