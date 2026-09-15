#!/usr/bin/env python3
"""Apply the fail-closed protected-split conflict policy to closure evidence.

This stage runs after the base closure evidence builder. It never moves individual
clips between protected upstream splits. If a ready recording group contains more
than one recognized original split, the complete group is quarantined from
coverage and frozen corpus membership while remaining durable ledger evidence.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from echo.data_foundry.coverage_policy import evaluate_coverage, load_coverage_policy
from echo.data_foundry.splits import SplitRatios, assign_group

ROOT = Path(__file__).resolve().parents[2]
MAT = ROOT / "MK1/mining-site/materialization"
LEDGER = MAT / "canonical-release-safe-asset-ledger.jsonl"
SPLIT_POLICY = ROOT / "configs/data_foundry/split_policy.v1.json"
COVERAGE_POLICY = ROOT / "configs/data_foundry/coverage_policy.v1.json"
DEDUP = MAT / "global-dedup-audit.json"
GROUP_AUDIT = MAT / "recording-family-audit.json"
OUT_SPLIT = MAT / "split-integrity.json"
OUT_COVERAGE = MAT / "coverage-gate.json"
OUT_FREEZE1 = MAT / "corpus-freeze-1.validation.json"
OUT_FREEZE2 = MAT / "corpus-freeze-2.validation.json"
OUT_REPRO = MAT / "corpus-reproducibility.json"

QUARANTINE = "quarantine"
EXPECTED_STRATEGY = "quarantine_entire_recording_group"


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object: {path}")
    return payload


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"expected object at {path}:{number}")
            rows.append(row)
    return rows


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _ready(row: Mapping[str, Any]) -> bool:
    return (
        row.get("rights_status") == "ALLOW_RELEASE_SAFE"
        and row.get("stage_status") == "READY_FOR_GLOBAL_DEDUP"
        and not (row.get("blocking_reasons") or [])
        and bool(row.get("media_sha256"))
        and int(row.get("byte_size") or 0) > 0
        and isinstance(row.get("audio_probe"), Mapping)
        and row.get("audio_probe", {}).get("ok") is True
        and bool(row.get("recording_group_id"))
    )


def split_plan_with_quarantine(
    rows: list[dict[str, Any]], split_policy: Mapping[str, Any]
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    strategy = str(split_policy.get("protected_original_split_conflict_strategy") or "")
    if strategy != EXPECTED_STRATEGY:
        raise ValueError(
            "protected original split conflicts require explicit "
            f"{EXPECTED_STRATEGY!r} strategy, got {strategy!r}"
        )

    original_map = {
        str(key).lower(): str(value)
        for key, value in (split_policy.get("original_split_map") or {}).items()
    }
    ratios_cfg = split_policy.get("fallback_group_hash_ratios") or {}
    ratios = SplitRatios(
        train=float(ratios_cfg.get("train", 0.7)),
        validation=float(ratios_cfg.get("validation", 0.15)),
        test=float(ratios_cfg.get("test", 0.15)),
    )
    seed = str(split_policy.get("seed") or "")

    by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if _ready(row):
            by_group[str(row["recording_group_id"])].append(row)

    assignments: dict[str, str] = {}
    conflicts: list[dict[str, Any]] = []
    for group, items in sorted(by_group.items()):
        if any(bool(item.get("field_holdout")) for item in items):
            assignments[group] = "field_holdout"
            continue

        originals = sorted({
            original_map[str(item.get("original_split") or "").lower()]
            for item in items
            if str(item.get("original_split") or "").lower() in original_map
        })
        if len(originals) > 1:
            assignments[group] = QUARANTINE
            conflicts.append({
                "recording_group_id": group,
                "recognized_original_splits": originals,
                "asset_count": len(items),
                "asset_ids": sorted(str(item["ledger_asset_id"]) for item in items),
            })
            continue
        if originals:
            assignments[group] = originals[0]
        else:
            assignments[group] = assign_group(group, seed=seed, ratios=ratios)

    return assignments, conflicts


def build_quarantined_split_audit(
    rows: list[dict[str, Any]],
    split_policy: Mapping[str, Any],
    dedup: Mapping[str, Any],
    group_audit: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    assignments, conflicts = split_plan_with_quarantine(rows, split_policy)
    ready_rows = [row for row in rows if _ready(row)]
    split_counts = Counter(
        assignments.get(str(row["recording_group_id"]), "UNASSIGNED")
        for row in ready_rows
    )
    quarantined_groups = {str(item["recording_group_id"]) for item in conflicts}
    quarantined_rows = [
        row for row in ready_rows
        if str(row["recording_group_id"]) in quarantined_groups
    ]
    development_rows = [
        row for row in ready_rows
        if assignments.get(str(row["recording_group_id"])) != QUARANTINE
    ]

    gaps: list[str] = []
    if dedup.get("status") != "PASS":
        gaps.append("UPSTREAM_GLOBAL_DEDUP_NOT_PASS")
    if group_audit.get("status") != "PASS":
        gaps.append("UPSTREAM_RECORDING_FAMILY_AUDIT_NOT_PASS")
    if any(value == "UNASSIGNED" for value in split_counts):
        gaps.append("ELIGIBLE_ASSET_WITHOUT_SPLIT")

    return (
        {
            "schema_version": "echo.split-integrity.v2",
            "status": "PASS" if not gaps else "FAIL",
            "policy_id": split_policy.get("policy_id"),
            "protected_original_split_conflict_strategy": EXPECTED_STRATEGY,
            "ready_candidate_asset_count": len(ready_rows),
            "eligible_asset_count": len(development_rows),
            "recording_family_assignment_count": len(assignments),
            "split_asset_counts": dict(sorted(split_counts.items())),
            "original_split_conflict_count": len(conflicts),
            "original_split_conflicts_quarantined": len(conflicts),
            "quarantined_asset_count": len(quarantined_rows),
            "quarantined_recording_family_count": len(quarantined_groups),
            "quarantine_identity_sha256": _digest(conflicts),
            "quarantine_groups": conflicts,
            "assignment_sha256": _digest(sorted(assignments.items())),
            "gap_codes": sorted(gaps),
            "split_policy_sha256": _sha(SPLIT_POLICY),
            "ledger_sha256": _sha(LEDGER),
            "boundary": (
                "Conflicting protected original splits quarantine the complete acoustic "
                "recording group. No member is remapped; quarantined rows remain source/ledger "
                "evidence but cannot satisfy development coverage or frozen corpus membership."
            ),
        },
        assignments,
    )


def _coverage_rows(
    rows: list[dict[str, Any]], assignments: Mapping[str, str]
) -> list[dict[str, Any]]:
    translated: list[dict[str, Any]] = []
    for row in rows:
        if not _ready(row):
            continue
        group = str(row.get("recording_group_id") or "")
        assignment = assignments.get(group)
        if assignment == QUARANTINE:
            continue
        probe = row.get("audio_probe") if isinstance(row.get("audio_probe"), Mapping) else {}
        translated.append({
            "asset_id": row["ledger_asset_id"],
            "sha256": row.get("media_sha256"),
            "source_dataset": row.get("underlying_source_family") or row.get("source_dataset"),
            "recording_group_id": group,
            "echo_split": assignment,
            "field_holdout": bool(row.get("field_holdout")),
            "duration_seconds": float(probe.get("duration_seconds") or 0.0),
            "license_id": row.get("license_id"),
            "echo_labels": list(row.get("echo_labels") or []),
            "label_provenance": ";".join(str(v) for v in (row.get("label_provenance") or [])),
            "extra": {
                "audio_probe": dict(probe),
                "confuses": list(row.get("hard_negative_for") or []),
                "near_duplicate_fingerprint": (
                    (row.get("canonical_fingerprint") or {}).get("canonical_pcm_sha256")
                    if isinstance(row.get("canonical_fingerprint"), Mapping)
                    else None
                ),
            },
        })
    return translated


def build_quarantined_coverage(
    rows: list[dict[str, Any]],
    assignments: Mapping[str, str],
    split_audit: Mapping[str, Any],
    dedup: Mapping[str, Any],
    group_audit: Mapping[str, Any],
) -> dict[str, Any]:
    policy = load_coverage_policy(COVERAGE_POLICY)
    translated = _coverage_rows(rows, assignments)
    result = evaluate_coverage(translated, policy=policy, profile="release_safe")
    failures = list(result.get("failures") or [])
    for code, payload in (
        ("UPSTREAM_GLOBAL_DEDUP_NOT_PASS", dedup),
        ("UPSTREAM_RECORDING_FAMILY_AUDIT_NOT_PASS", group_audit),
        ("UPSTREAM_SPLIT_INTEGRITY_NOT_PASS", split_audit),
    ):
        if payload.get("status") != "PASS" and not any(item.get("code") == code for item in failures):
            failures.append({"code": code})
    result["failures"] = failures
    result["gap_codes"] = sorted({str(item["code"]) for item in failures})
    result["status"] = "PASS" if not failures else "FAIL"
    result["ledger_sha256"] = _sha(LEDGER)
    result["coverage_policy_sha256"] = _sha(COVERAGE_POLICY)
    result["split_policy_sha256"] = _sha(SPLIT_POLICY)
    result["quarantined_split_conflict_asset_count"] = int(split_audit.get("quarantined_asset_count") or 0)
    result["development_asset_count"] = len(translated)
    result["note"] = (
        "Coverage excludes whole acoustic groups quarantined by protected original-split "
        "conflicts and counts only release-safe ready rows by underlying acoustic source family."
    )
    return result


def build_quarantined_freezes(
    rows: list[dict[str, Any]],
    assignments: Mapping[str, str],
    dedup: Mapping[str, Any],
    group_audit: Mapping[str, Any],
    split_audit: Mapping[str, Any],
    coverage: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    blockers = [
        name
        for name, payload in (
            ("GLOBAL_DEDUP", dedup),
            ("RECORDING_FAMILY", group_audit),
            ("SPLIT_INTEGRITY", split_audit),
            ("COVERAGE", coverage),
        )
        if payload.get("status") != "PASS"
    ]
    eligible = [
        row for row in rows
        if _ready(row)
        and assignments.get(str(row.get("recording_group_id") or "")) != QUARANTINE
    ]
    membership = [{
        "asset_id": row["ledger_asset_id"],
        "media_sha256": row["media_sha256"],
        "recording_group_id": row["recording_group_id"],
        "split": assignments.get(str(row["recording_group_id"])),
        "echo_labels": sorted(row.get("echo_labels") or []),
        "hard_negative_for": sorted(row.get("hard_negative_for") or []),
        "underlying_source_family": row.get("underlying_source_family"),
    } for row in eligible]
    identity = _digest(sorted(membership, key=lambda row: row["asset_id"]))
    status = "PASS" if not blockers else "FAIL"
    gaps = [] if not blockers else [f"UPSTREAM_{name}_NOT_PASS" for name in blockers]
    base = {
        "schema_version": "echo.corpus-freeze-validation.v2",
        "status": status,
        "asset_count": len(membership),
        "quarantined_asset_count": int(split_audit.get("quarantined_asset_count") or 0),
        "semantic_identity_sha256": identity,
        "ledger_sha256": _sha(LEDGER),
        "split_assignment_sha256": _digest(sorted(assignments.items())),
        "split_policy_sha256": _sha(SPLIT_POLICY),
        "gap_codes": gaps,
        "boundary": "No quarantined split-conflict group is frozen; benchmark handoff still requires every upstream closure gate PASS.",
    }
    freeze1 = {**base, "freeze_id": "MK1-CORPUS-FREEZE-1"}
    freeze2 = {**base, "freeze_id": "MK1-CORPUS-FREEZE-2"}
    reproducibility = {
        "schema_version": "echo.corpus-reproducibility.v2",
        "status": "PASS" if status == "PASS" and freeze1["semantic_identity_sha256"] == freeze2["semantic_identity_sha256"] else "FAIL",
        "freeze_1_identity": freeze1["semantic_identity_sha256"],
        "freeze_2_identity": freeze2["semantic_identity_sha256"],
        "identity_match": freeze1["semantic_identity_sha256"] == freeze2["semantic_identity_sha256"],
        "quarantine_identity_sha256": split_audit.get("quarantine_identity_sha256"),
        "gap_codes": [] if status == "PASS" else ["UPSTREAM_FREEZE_NOT_ELIGIBLE"],
        "note": "Both freezes use identical whole-group split quarantine semantics; final certificate review binds these identities to exact durable evidence.",
    }
    return freeze1, freeze2, reproducibility


def main() -> int:
    for path in (LEDGER, SPLIT_POLICY, COVERAGE_POLICY, DEDUP, GROUP_AUDIT):
        if not path.is_file():
            raise SystemExit(f"missing split-quarantine input: {path.relative_to(ROOT)}")

    rows = _jsonl(LEDGER)
    split_policy = _json(SPLIT_POLICY)
    dedup = _json(DEDUP)
    group_audit = _json(GROUP_AUDIT)
    split_audit, assignments = build_quarantined_split_audit(rows, split_policy, dedup, group_audit)
    coverage = build_quarantined_coverage(rows, assignments, split_audit, dedup, group_audit)
    freeze1, freeze2, reproducibility = build_quarantined_freezes(
        rows, assignments, dedup, group_audit, split_audit, coverage
    )

    for path, payload in (
        (OUT_SPLIT, split_audit),
        (OUT_COVERAGE, coverage),
        (OUT_FREEZE1, freeze1),
        (OUT_FREEZE2, freeze2),
        (OUT_REPRO, reproducibility),
    ):
        _write(path, payload)

    print(json.dumps({
        "split_integrity": split_audit["status"],
        "quarantined_groups": split_audit["quarantined_recording_family_count"],
        "quarantined_assets": split_audit["quarantined_asset_count"],
        "coverage": coverage["status"],
        "freeze_1": freeze1["status"],
        "freeze_2": freeze2["status"],
        "reproducibility": reproducibility["status"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
