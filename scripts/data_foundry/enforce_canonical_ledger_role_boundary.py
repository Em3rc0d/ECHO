#!/usr/bin/env python3
"""Enforce the release-safe corpus admission boundary on the canonical ledger.

Source materialization reports remain the durable evidence inventory. The canonical
ledger is the input to global dedup/group/split/coverage and therefore must contain
only assets with an exact ECHO positive role or an explicitly governed hard-negative
role that are also release-safe and free of unresolved admission blockers.

This boundary runs *before* global recording-group resolution. The single
GROUPING_GLOBAL_AUDIT_REQUIRED marker is therefore a deferred pre-grouping gate, not
a final admission failure: the immediately following resolver must remove it or the
later closure audits fail closed. All other unresolved blockers remain quarantined.

Rows rejected here are quarantined only from the corpus-facing ledger. Their source
materialization/provenance evidence remains durable elsewhere; this step never
promotes a disputed semantic role, rewrites a license, invents a source family, or
lowers a coverage floor.
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

RELEASE_SAFE_RIGHTS_STATUS = "ALLOW_RELEASE_SAFE"
DEFERRED_PRE_GROUPING_BLOCKERS = frozenset({"GROUPING_GLOBAL_AUDIT_REQUIRED"})


def has_governed_corpus_role(row: Mapping[str, Any]) -> bool:
    positives = {str(v) for v in (row.get("echo_labels") or [])}
    negatives = {str(v) for v in (row.get("hard_negative_for") or [])}
    return bool((positives | negatives) & set(TARGET_LABELS))


def unresolved_admission_blockers(row: Mapping[str, Any]) -> set[str]:
    blockers = {str(v) for v in (row.get("blocking_reasons") or [])}
    return blockers - DEFERRED_PRE_GROUPING_BLOCKERS


def corpus_admission_rejection(row: Mapping[str, Any]) -> str | None:
    """Return the fail-closed rejection class, or None when pre-grouping admissible.

    Classification is deliberately conservative and ordered:
    1. rows without a governed positive/HN role are review-only evidence;
    2. governed rows must be explicitly release-safe;
    3. governed release-safe rows may carry only the known pre-grouping grouping gate.

    The deferred grouping marker is not silently waived: the next pipeline stage must
    resolve it, and global grouping/dedup/closure audits independently verify that.
    """

    if not has_governed_corpus_role(row):
        return "REVIEW_ONLY_NO_GOVERNED_ROLE"
    if str(row.get("rights_status") or "") != RELEASE_SAFE_RIGHTS_STATUS:
        return "NOT_RELEASE_SAFE"
    if unresolved_admission_blockers(row):
        return "UNRESOLVED_ADMISSION_BLOCKER"
    return None


def apply_role_boundary(rows: Iterable[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    removed: list[tuple[Mapping[str, Any], str]] = []

    for row in rows:
        rejection = corpus_admission_rejection(row)
        if rejection is None:
            kept.append(dict(row))
        else:
            removed.append((row, rejection))

    removed_sources = Counter(
        str(row.get("source_dataset") or "UNKNOWN") for row, _ in removed
    )
    removed_blockers = Counter(
        str(reason)
        for row, _ in removed
        for reason in (row.get("blocking_reasons") or [])
    )
    removed_rights = Counter(
        str(row.get("rights_status") or "MISSING") for row, _ in removed
    )
    rejection_counts = Counter(rejection for _, rejection in removed)
    retained_deferred = Counter(
        str(reason)
        for row in kept
        for reason in (row.get("blocking_reasons") or [])
        if str(reason) in DEFERRED_PRE_GROUPING_BLOCKERS
    )

    audit = {
        "schema_version": "echo.canonical-ledger-role-boundary.v3",
        "policy": "release_safe_exact_positive_or_governed_hard_negative_required",
        "input_rows": len(kept) + len(removed),
        "retained_rows": len(kept),
        "removed_rows": len(removed),
        "removed_review_only_rows": rejection_counts["REVIEW_ONLY_NO_GOVERNED_ROLE"],
        "removed_non_release_safe_rows": rejection_counts["NOT_RELEASE_SAFE"],
        "removed_unresolved_blocker_rows": rejection_counts["UNRESOLVED_ADMISSION_BLOCKER"],
        "removed_rejection_counts": dict(sorted(rejection_counts.items())),
        "removed_source_counts": dict(sorted(removed_sources.items())),
        "removed_blocking_reason_counts": dict(sorted(removed_blockers.items())),
        "removed_rights_status_counts": dict(sorted(removed_rights.items())),
        "deferred_pre_grouping_blockers": sorted(DEFERRED_PRE_GROUPING_BLOCKERS),
        "retained_deferred_blocker_counts": dict(sorted(retained_deferred.items())),
        "source_evidence_retained_elsewhere": True,
        "boundary_note": (
            "Removed rows remain in source materialization/review evidence. This step does not "
            "promote disputed labels, rewrite licenses, invent source families, lower coverage "
            "floors, or merge acoustic content. GROUPING_GLOBAL_AUDIT_REQUIRED alone is retained "
            "only because global recording-group resolution runs immediately next and must clear it; "
            "all other unresolved blockers are quarantined fail-closed."
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
        "The corpus-facing canonical ledger contains only explicitly release-safe assets with exact "
        "positive or governed hard-negative roles and no unresolved admission blockers other than "
        "the explicitly deferred pre-grouping marker. Quarantined rows remain durable source evidence "
        "and are not silently relabeled. The following grouping resolver must clear the deferred marker; "
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
        "removed_rows": audit["removed_rows"],
        "removed_review_only_rows": audit["removed_review_only_rows"],
        "removed_non_release_safe_rows": audit["removed_non_release_safe_rows"],
        "removed_unresolved_blocker_rows": audit["removed_unresolved_blocker_rows"],
        "retained_deferred_blocker_counts": audit["retained_deferred_blocker_counts"],
        "remaining_blocking_reason_counts": refreshed.get("blocking_reason_counts", {}),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
