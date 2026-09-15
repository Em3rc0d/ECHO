#!/usr/bin/env python3
"""Remove review-only evidence rows from the corpus-facing canonical ledger.

Source materialization reports remain the durable evidence inventory. The canonical
ledger is the input to global dedup/group/split/coverage and therefore must contain
only assets with an exact ECHO positive role or an explicitly governed hard-negative
role. Downloadability/materialization alone is never corpus admission.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from echo.data_foundry.contracts import TARGET_LABELS
from echo.data_foundry.ledger import summarize_ledger, validate_ledger

ROOT = Path(__file__).resolve().parents[2]
MATERIALIZATION = ROOT / "MK1/mining-site/materialization"
LEDGER = MATERIALIZATION / "canonical-release-safe-asset-ledger.jsonl"
SUMMARY = MATERIALIZATION / "canonical-release-safe-asset-ledger-summary.json"


def has_governed_corpus_role(row: Mapping[str, Any]) -> bool:
    positives = {str(v) for v in (row.get("echo_labels") or [])}
    negatives = {str(v) for v in (row.get("hard_negative_for") or [])}
    return bool((positives | negatives) & set(TARGET_LABELS))


def apply_role_boundary(rows: Iterable[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    removed: list[Mapping[str, Any]] = []
    for row in rows:
        if has_governed_corpus_role(row):
            kept.append(dict(row))
        else:
            removed.append(row)

    removed_sources = Counter(str(row.get("source_dataset") or "UNKNOWN") for row in removed)
    removed_blockers = Counter(
        str(reason)
        for row in removed
        for reason in (row.get("blocking_reasons") or [])
    )
    audit = {
        "schema_version": "echo.canonical-ledger-role-boundary.v1",
        "policy": "exact_positive_or_governed_hard_negative_required",
        "input_rows": len(kept) + len(removed),
        "retained_rows": len(kept),
        "removed_review_only_rows": len(removed),
        "removed_source_counts": dict(sorted(removed_sources.items())),
        "removed_blocking_reason_counts": dict(sorted(removed_blockers.items())),
        "source_evidence_retained_elsewhere": True,
        "boundary_note": (
            "Removed rows remain in source materialization/review evidence. This step does not "
            "promote labels, invent source families, lower coverage floors, or merge acoustic content."
        ),
    }
    return kept, audit


def read_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with LEDGER.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"ledger row must be object at line {line_number}")
            rows.append(value)
    return rows


def main() -> int:
    if not LEDGER.is_file() or not SUMMARY.is_file():
        raise SystemExit("canonical ledger and summary must exist before role-boundary enforcement")

    source_rows = validate_ledger(read_rows())
    kept, audit = apply_role_boundary(source_rows)
    kept = validate_ledger(kept)

    previous = json.loads(SUMMARY.read_text(encoding="utf-8"))
    refreshed = dict(previous)
    refreshed.update(summarize_ledger(kept))
    refreshed["role_boundary"] = audit
    refreshed["certification_boundary"] = (
        "The corpus-facing canonical ledger contains only exact positive or governed hard-negative "
        "roles. Review-only materializations remain source evidence and are not corpus admission. "
        "READY_FOR_GLOBAL_DEDUP still does not mean ADMITTED_RELEASE_SAFE or CERTIFIED."
    )

    with LEDGER.open("w", encoding="utf-8") as handle:
        for row in kept:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    SUMMARY.write_text(json.dumps(refreshed, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PASS",
        "input_rows": audit["input_rows"],
        "retained_rows": audit["retained_rows"],
        "removed_review_only_rows": audit["removed_review_only_rows"],
        "remaining_blocking_reason_counts": refreshed.get("blocking_reason_counts", {}),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
