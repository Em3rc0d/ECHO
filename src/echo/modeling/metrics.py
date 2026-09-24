"""Dependency-free multilabel benchmark metrics.

Thresholds are tuned on validation data only and then applied unchanged to test.
Unknown/masked labels are excluded from every metric.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class BinaryMetrics:
    threshold: float
    support_positive: int
    support_negative: int
    tp: int
    fp: int
    tn: int
    fn: int
    precision: float
    recall: float
    f1: float
    false_positive_rate: float
    accuracy: float

    def to_dict(self) -> dict:
        return {
            "threshold": self.threshold,
            "support_positive": self.support_positive,
            "support_negative": self.support_negative,
            "tp": self.tp,
            "fp": self.fp,
            "tn": self.tn,
            "fn": self.fn,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "false_positive_rate": self.false_positive_rate,
            "accuracy": self.accuracy,
        }


def _safe_div(num: int | float, den: int | float) -> float:
    return float(num) / float(den) if den else 0.0


def evaluate_binary(
    probabilities: Sequence[float],
    targets: Sequence[int],
    *,
    threshold: float,
) -> BinaryMetrics:
    if len(probabilities) != len(targets):
        raise ValueError("probabilities and targets length mismatch")
    if not probabilities:
        raise ValueError("cannot evaluate an empty target set")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be within [0, 1]")

    tp = fp = tn = fn = 0
    for probability, target in zip(probabilities, targets, strict=True):
        if target not in {0, 1}:
            raise ValueError("binary targets must be 0 or 1")
        prediction = float(probability) >= threshold
        if prediction and target == 1:
            tp += 1
        elif prediction and target == 0:
            fp += 1
        elif not prediction and target == 0:
            tn += 1
        else:
            fn += 1

    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2.0 * precision * recall, precision + recall)
    return BinaryMetrics(
        threshold=threshold,
        support_positive=tp + fn,
        support_negative=tn + fp,
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
        precision=precision,
        recall=recall,
        f1=f1,
        false_positive_rate=_safe_div(fp, fp + tn),
        accuracy=_safe_div(tp + tn, tp + fp + tn + fn),
    )


def tune_threshold(
    probabilities: Sequence[float],
    targets: Sequence[int],
    *,
    candidates: Iterable[float] | None = None,
) -> BinaryMetrics:
    grid = (
        tuple(float(v) for v in candidates)
        if candidates is not None
        else tuple(i / 100.0 for i in range(5, 96, 5))
    )
    if not grid:
        raise ValueError("threshold candidate grid is empty")

    metrics = [
        evaluate_binary(probabilities, targets, threshold=threshold)
        for threshold in grid
    ]
    # Prefer F1, then recall, then lower false-positive rate, then the more
    # conservative (higher) threshold for deterministic tie-breaking.
    return max(
        metrics,
        key=lambda row: (
            row.f1,
            row.recall,
            -row.false_positive_rate,
            row.threshold,
        ),
    )
