"""Train/evaluate the small ECHO head on frozen pretrained embeddings."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping, Sequence

from .manifest import BenchmarkRow, MVP_TARGETS
from .metrics import evaluate_binary, tune_threshold


@dataclass(frozen=True)
class HeadTrainingConfig:
    epochs: int = 80
    batch_size: int = 64
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    hidden_dim: int = 256
    dropout: float = 0.2
    patience: int = 12
    seed: int = 1337


def _require_stack():
    try:
        import numpy as np
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "Embedding benchmark requires numpy and torch; install the 'mvp' extra"
        ) from exc
    return np, torch


def supervision_arrays(rows: Sequence[BenchmarkRow]):
    np, _torch = _require_stack()
    y = np.zeros((len(rows), len(MVP_TARGETS)), dtype=np.float32)
    mask = np.zeros_like(y)
    for i, row in enumerate(rows):
        for j, target in enumerate(MVP_TARGETS):
            value = row.supervision.get(target)
            if value is None:
                continue
            y[i, j] = float(value)
            mask[i, j] = 1.0
    return y, mask


def _metrics_for_split(probabilities, y, mask, thresholds: Mapping[str, float]):
    per_class = {}
    for j, target in enumerate(MVP_TARGETS):
        known = mask[:, j] > 0.5
        probs = probabilities[known, j].tolist()
        labels = y[known, j].astype(int).tolist()
        if not labels:
            raise ValueError(f"no known supervision for {target}")
        per_class[target] = evaluate_binary(
            probs,
            labels,
            threshold=float(thresholds[target]),
        ).to_dict()
    macro_f1 = sum(row["f1"] for row in per_class.values()) / len(per_class)
    macro_recall = sum(row["recall"] for row in per_class.values()) / len(per_class)
    macro_precision = sum(row["precision"] for row in per_class.values()) / len(per_class)
    macro_fpr = (
        sum(row["false_positive_rate"] for row in per_class.values())
        / len(per_class)
    )
    return {
        "per_class": per_class,
        "macro_f1": macro_f1,
        "macro_recall": macro_recall,
        "macro_precision": macro_precision,
        "macro_false_positive_rate": macro_fpr,
    }


def _tune(probabilities, y, mask):
    thresholds = {}
    validation = {}
    for j, target in enumerate(MVP_TARGETS):
        known = mask[:, j] > 0.5
        probs = probabilities[known, j].tolist()
        labels = y[known, j].astype(int).tolist()
        tuned = tune_threshold(probs, labels)
        thresholds[target] = tuned.threshold
        validation[target] = tuned.to_dict()
    macro_f1 = sum(row["f1"] for row in validation.values()) / len(validation)
    return thresholds, validation, macro_f1


def train_embedding_head(
    *,
    features,
    rows: Sequence[BenchmarkRow],
    input_dim: int,
    config: HeadTrainingConfig,
    device: str = "cpu",
):
    np, torch = _require_stack()
    import torch.nn as nn

    if features.shape != (len(rows), input_dim):
        raise ValueError(
            f"features shape {features.shape} != {(len(rows), input_dim)}"
        )

    torch.manual_seed(config.seed)
    np.random.seed(config.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(config.seed)

    split_indices = {
        split: np.asarray(
            [i for i, row in enumerate(rows) if row.split == split],
            dtype=np.int64,
        )
        for split in ("train", "validation", "test")
    }
    for split, indices in split_indices.items():
        if indices.size == 0:
            raise ValueError(f"benchmark split {split} is empty")

    y, mask = supervision_arrays(rows)
    x_tensor = torch.as_tensor(features, dtype=torch.float32)
    y_tensor = torch.as_tensor(y, dtype=torch.float32)
    mask_tensor = torch.as_tensor(mask, dtype=torch.float32)

    class EmbeddingHead(nn.Module):
        def __init__(self):
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(input_dim, config.hidden_dim),
                nn.ReLU(),
                nn.Dropout(config.dropout),
                nn.Linear(config.hidden_dim, len(MVP_TARGETS)),
            )

        def forward(self, x):
            return self.network(x)

    model = EmbeddingHead().to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )

    train_idx = split_indices["train"]
    train_y = y[train_idx]
    train_mask = mask[train_idx]
    pos_weights = []
    for j in range(len(MVP_TARGETS)):
        known = train_mask[:, j] > 0.5
        positives = float(train_y[known, j].sum())
        negatives = float(known.sum() - positives)
        pos_weights.append(negatives / positives if positives > 0 else 1.0)
    pos_weight = torch.tensor(pos_weights, dtype=torch.float32, device=device)
    loss_fn = nn.BCEWithLogitsLoss(reduction="none", pos_weight=pos_weight)

    best = {
        "macro_f1": -1.0,
        "epoch": 0,
        "state_dict": None,
        "thresholds": None,
        "validation_per_class": None,
    }
    stale_epochs = 0

    generator = torch.Generator(device="cpu")
    generator.manual_seed(config.seed)

    for epoch in range(1, config.epochs + 1):
        model.train()
        permutation = train_idx[
            torch.randperm(len(train_idx), generator=generator).numpy()
        ]
        for start in range(0, len(permutation), config.batch_size):
            batch = permutation[start : start + config.batch_size]
            xb = x_tensor[batch].to(device)
            yb = y_tensor[batch].to(device)
            mb = mask_tensor[batch].to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(xb)
            raw = loss_fn(logits, yb)
            denominator = mb.sum().clamp_min(1.0)
            loss = (raw * mb).sum() / denominator
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            val_idx = split_indices["validation"]
            val_logits = model(x_tensor[val_idx].to(device))
            val_probs = torch.sigmoid(val_logits).cpu().numpy()
        val_y = y[val_idx]
        val_mask = mask[val_idx]
        thresholds, validation_per_class, macro_f1 = _tune(
            val_probs, val_y, val_mask
        )

        if macro_f1 > best["macro_f1"] + 1e-12:
            best = {
                "macro_f1": macro_f1,
                "epoch": epoch,
                "state_dict": deepcopy(model.state_dict()),
                "thresholds": thresholds,
                "validation_per_class": validation_per_class,
            }
            stale_epochs = 0
        else:
            stale_epochs += 1
            if stale_epochs >= config.patience:
                break

    if best["state_dict"] is None or best["thresholds"] is None:
        raise RuntimeError("training failed to produce a valid checkpoint")

    model.load_state_dict(best["state_dict"])
    model.eval()

    report = {
        "targets": list(MVP_TARGETS),
        "selected_epoch": best["epoch"],
        "validation_thresholds": best["thresholds"],
        "validation": {
            "per_class": best["validation_per_class"],
            "macro_f1": best["macro_f1"],
        },
        "training": {
            "config": {
                "epochs": config.epochs,
                "batch_size": config.batch_size,
                "learning_rate": config.learning_rate,
                "weight_decay": config.weight_decay,
                "hidden_dim": config.hidden_dim,
                "dropout": config.dropout,
                "patience": config.patience,
                "seed": config.seed,
            },
            "positive_weights": {
                target: float(pos_weights[j])
                for j, target in enumerate(MVP_TARGETS)
            },
        },
    }

    for split in ("validation", "test"):
        indices = split_indices[split]
        with torch.no_grad():
            logits = model(x_tensor[indices].to(device))
            probabilities = torch.sigmoid(logits).cpu().numpy()
        report[split] = _metrics_for_split(
            probabilities,
            y[indices],
            mask[indices],
            best["thresholds"],
        )

    return model, report
