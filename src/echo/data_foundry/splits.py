"""Deterministic, group-aware split planning for the ECHO Data Foundry."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Iterable, Mapping


@dataclass(frozen=True)
class SplitRatios:
    train: float
    validation: float
    test: float

    def __post_init__(self) -> None:
        values = (self.train, self.validation, self.test)
        if any((not math.isfinite(v) or v < 0.0 or v > 1.0) for v in values):
            raise ValueError("split ratios must be finite values in [0, 1]")
        if not math.isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("split ratios must sum to 1.0")
        if self.train <= 0.0:
            raise ValueError("training ratio must be positive")


def _unit_interval(seed: str, group_id: str) -> float:
    if not group_id:
        raise ValueError("group_id must not be empty")
    digest = hashlib.sha256(f"{seed}\0{group_id}".encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return value / float(2**64)


def assign_group(group_id: str, *, seed: str, ratios: SplitRatios) -> str:
    """Return a stable split for one independent group.

    Ratios are explicit inputs.  No project-wide default is intentionally
    embedded here because changing the benchmark split must be an auditable
    configuration change.
    """

    point = _unit_interval(seed, group_id)
    if point < ratios.train:
        return "train"
    if point < ratios.train + ratios.validation:
        return "validation"
    return "test"


def plan_groups(
    group_ids: Iterable[str], *, seed: str, ratios: SplitRatios
) -> dict[str, str]:
    return {
        group_id: assign_group(group_id, seed=seed, ratios=ratios)
        for group_id in sorted(set(group_ids))
    }


def audit_group_splits(assignments: Mapping[str, str]) -> None:
    allowed = {"train", "validation", "test", "field_holdout"}
    for group_id, split in assignments.items():
        if not group_id:
            raise ValueError("split manifest contains an empty group_id")
        if split not in allowed:
            raise ValueError(f"unsupported split {split!r} for group {group_id!r}")


def assert_no_cross_split_hashes(
    rows: Iterable[Mapping[str, object]],
) -> None:
    """Raise if exact content bytes appear across protected split boundaries."""

    seen: dict[str, str] = {}
    for row in rows:
        digest = str(row.get("sha256") or "")
        split = str(row.get("echo_split") or "")
        if not digest or not split:
            continue
        previous = seen.get(digest)
        if previous is not None and previous != split:
            raise ValueError(
                f"exact content hash {digest} crosses splits: {previous} vs {split}"
            )
        seen[digest] = split
