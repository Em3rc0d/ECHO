"""Manual semantic-review decisions for ECHO Data Foundry.

Review decisions are explicit evidence objects.  They never bypass license
policy, file hashing or split/dedup gates; they only resolve semantic ambiguity
for an already identified asset.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import TARGET_LABELS


@dataclass(frozen=True)
class ReviewDecision:
    asset_id: str
    approved: bool
    echo_labels: tuple[str, ...]
    reviewer: str
    reviewed_at_utc: str
    rationale: str
    evidence_ref: str | None = None

    def __post_init__(self) -> None:
        unknown = set(self.echo_labels) - set(TARGET_LABELS)
        if unknown:
            raise ValueError(f"unknown ECHO labels in review: {sorted(unknown)}")
        if not self.asset_id:
            raise ValueError("review asset_id is required")
        if not self.reviewer:
            raise ValueError("reviewer is required")
        if not self.reviewed_at_utc:
            raise ValueError("reviewed_at_utc is required")
        if not self.rationale:
            raise ValueError("review rationale is required")


def load_review_decisions(path: str | Path) -> dict[str, ReviewDecision]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema_version") != "echo.review-decisions.v1":
        raise ValueError("unsupported review decision schema")
    raw = payload.get("decisions", [])
    if not isinstance(raw, list):
        raise ValueError("review decisions must be an array")
    result: dict[str, ReviewDecision] = {}
    for row in raw:
        if not isinstance(row, Mapping):
            raise ValueError("review decision must be an object")
        decision = ReviewDecision(
            asset_id=str(row.get("asset_id") or ""),
            approved=bool(row.get("approved", False)),
            echo_labels=tuple(sorted({str(v) for v in row.get("echo_labels", [])})),
            reviewer=str(row.get("reviewer") or ""),
            reviewed_at_utc=str(row.get("reviewed_at_utc") or ""),
            rationale=str(row.get("rationale") or ""),
            evidence_ref=(str(row["evidence_ref"]) if row.get("evidence_ref") else None),
        )
        if decision.asset_id in result:
            raise ValueError(f"duplicate review decision for {decision.asset_id}")
        result[decision.asset_id] = decision
    return result


def review_for(asset_id: str, decisions: Mapping[str, ReviewDecision] | None) -> ReviewDecision | None:
    if not decisions:
        return None
    return decisions.get(asset_id)
