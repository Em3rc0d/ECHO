#!/usr/bin/env python3
"""Enrich the canonical MK1 ledger with durable per-asset source evidence.

The builder intentionally consolidates source identities first. This second,
deterministic stage binds evidence that is produced while real bytes exist:
asset-level probes, canonical codec-independent fingerprints and governed hard
negative roles. It never invents missing evidence and never promotes ambiguous
semantics. Missing fingerprint evidence for an exact semantic role is a blocker
for global near-duplicate audit readiness.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from echo.data_foundry.contracts import TARGET_LABELS
from echo.data_foundry.ledger import file_sha256, summarize_ledger, validate_ledger
from echo.data_foundry.source_policy import load_dataset_certification
from scripts.data_foundry.build_canonical_asset_ledger import recompute_stage

ROOT = Path(__file__).resolve().parents[2]
MATERIALIZATION = ROOT / "MK1/mining-site/materialization"
LEDGER = MATERIALIZATION / "canonical-release-safe-asset-ledger.jsonl"
SUMMARY = MATERIALIZATION / "canonical-release-safe-asset-ledger-summary.json"
SOURCE_POLICY_PATH = ROOT / "configs/data_foundry/dataset_certification.v1.json"
HARD_NEGATIVE_MAPPING = ROOT / "configs/data_foundry/hard_negative_mapping.v1.json"

SONYC_TARGETS = MATERIALIZATION / "sonyc-v2.3-target-candidates.jsonl"
SONYC_CONFUSERS = MATERIALIZATION / "sonyc-v2.3-confuser-candidates.jsonl"
FREESOUND = MATERIALIZATION / "freesound-release-safe-materialization.json"
PUBLIC_GAP = MATERIALIZATION / "public-gap-assets-report.json"

DERIVED_FINGERPRINT_BLOCKER = "MISSING_CANONICAL_FINGERPRINT"
CROSS_TARGET_SEMANTIC_STATUS = "EXACT_POSITIVE_CROSS_TARGET_CONFUSER_001"
CROSS_TARGET_PROVENANCE_PREFIX = "MK1-HARD-NEGATIVE-MAPPING-001:CROSS_TARGET"
COMPATIBLE_HARD_NEGATIVE_STATUSES = {
    CROSS_TARGET_SEMANTIC_STATUS,
    "EXPLICIT_FSD50K_CONFUSER",
    "EXPLICIT_FSD50K_HARD_NEGATIVE_MAPPING_001",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"expected object at {path}:{line_number}")
            rows.append(value)
    return rows


def load_cross_target_confusers(path: Path = HARD_NEGATIVE_MAPPING) -> dict[str, tuple[str, ...]]:
    payload = read_json(path)
    if payload.get("policy_id") != "MK1-HARD-NEGATIVE-MAPPING-001":
        raise ValueError("unexpected hard-negative mapping policy")
    raw = payload.get("cross_target_exact_positive_confusers") or {}
    if not isinstance(raw, Mapping):
        raise ValueError("cross_target_exact_positive_confusers must be an object")
    result: dict[str, tuple[str, ...]] = {}
    for source_positive, target_values in raw.items():
        source_positive = str(source_positive)
        if source_positive not in TARGET_LABELS:
            raise ValueError(f"unknown cross-target source positive: {source_positive}")
        if not isinstance(target_values, list) or not target_values:
            raise ValueError(f"cross-target mapping must be a non-empty list: {source_positive}")
        targets = tuple(sorted({str(value) for value in target_values}))
        if any(target not in TARGET_LABELS for target in targets):
            raise ValueError(f"unknown cross-target destination for {source_positive}: {targets}")
        if source_positive in targets:
            raise ValueError(f"same-target hard negative forbidden: {source_positive}")
        result[source_positive] = targets
    return result


def technical_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}

    for path in (SONYC_TARGETS, SONYC_CONFUSERS):
        for row in read_jsonl(path):
            asset_id = f"sonyc-ust-v2:{row['source_asset_id']}"
            current = index.setdefault(asset_id, {})
            for key in ("byte_size", "audio_probe", "canonical_fingerprint"):
                value = row.get(key)
                if value is not None:
                    previous = current.get(key)
                    if previous is not None and previous != value:
                        raise ValueError(f"conflicting SONYC technical evidence for {asset_id}: {key}")
                    current[key] = value

    freesound = read_json(FREESOUND)
    for row in freesound.get("assets") or []:
        if row.get("status") != "RELEASE_SAFE_REAL_PREVIEW_MATERIALIZED":
            continue
        asset_id = f"echo-freesound-release-safe-v1:{row['sound_id']}"
        positive = {str(value) for value in row.get("targets") or [] if str(value) in TARGET_LABELS}
        hard_negative = {
            str(value) for value in row.get("hard_negative_for") or []
            if str(value) in TARGET_LABELS
        } - positive
        index[asset_id] = {
            "byte_size": row.get("size_bytes"),
            "audio_probe": row.get("audio_probe"),
            "canonical_fingerprint": row.get("canonical_fingerprint"),
            "hard_negative_for": sorted(hard_negative),
            "hard_negative_source_labels_by_target": row.get("hard_negative_source_labels_by_target") or {},
        }

    public_gap = read_json(PUBLIC_GAP)
    for row in public_gap.get("assets") or []:
        source_id = str(row.get("source_dataset") or "")
        if not source_id:
            continue
        asset_id = f"{source_id}:{row.get('asset_key')}"
        index[asset_id] = {
            "byte_size": row.get("size_bytes"),
            "audio_probe": row.get("audio_probe"),
            "canonical_fingerprint": row.get("canonical_fingerprint"),
        }
    return index


def merge_semantic_hard_negatives(row: dict[str, Any], evidence: Mapping[str, Any]) -> None:
    positives = {str(value) for value in row.get("echo_labels") or []}
    existing = {str(value) for value in row.get("hard_negative_for") or []}
    incoming = {
        str(value) for value in evidence.get("hard_negative_for") or []
        if str(value) in TARGET_LABELS
    }
    hard_negative = (existing | incoming) - positives
    row["hard_negative_for"] = sorted(hard_negative)
    if not incoming:
        return

    semantic = dict(row.get("semantic_status_by_target") or {})
    provenance = set(str(value) for value in row.get("label_provenance") or [])
    labels_by_target = evidence.get("hard_negative_source_labels_by_target") or {}
    for target in sorted(incoming - positives):
        source_labels = sorted(str(value) for value in labels_by_target.get(target) or [])
        semantic[target] = "EXPLICIT_FSD50K_CONFUSER"
        provenance.add(
            "MK1-HARD-NEGATIVE-MAPPING-001"
            + (":" + ",".join(source_labels) if source_labels else "")
        )
    row["semantic_status_by_target"] = dict(sorted(semantic.items()))
    row["label_provenance"] = sorted(provenance)
    row["candidate_targets"] = sorted(
        set(str(value) for value in row.get("candidate_targets") or []) | hard_negative
    )


def apply_cross_target_hard_negatives(
    row: dict[str, Any],
    mapping: Mapping[str, tuple[str, ...]],
) -> tuple[int, int]:
    """Attach governed cross-target negatives without overriding semantic conflicts.

    Returns ``(new_roles_attached, destinations_skipped_for_existing_semantics)``.
    A pre-existing review/conflict semantic for a destination is stronger evidence
    than the generic cross-target mapping and therefore blocks credit for only that
    destination while leaving other valid destinations available.
    """

    if row.get("rights_status") != "ALLOW_RELEASE_SAFE":
        return 0, 0
    fingerprint = row.get("canonical_fingerprint")
    if not (isinstance(fingerprint, Mapping) and fingerprint.get("vector_sha256")):
        return 0, 0

    positives = {
        str(value) for value in row.get("echo_labels") or []
        if str(value) in TARGET_LABELS
    }
    if not positives:
        return 0, 0

    semantic = dict(row.get("semantic_status_by_target") or {})
    eligible_derivations: list[tuple[str, str]] = []
    conflict_skips = 0
    for source_positive in sorted(positives):
        for target in mapping.get(source_positive, ()):
            if target in positives:
                continue
            previous = semantic.get(target)
            if previous and previous not in COMPATIBLE_HARD_NEGATIVE_STATUSES:
                conflict_skips += 1
                continue
            eligible_derivations.append((source_positive, target))

    derived = {target for _, target in eligible_derivations}
    if not derived:
        return 0, conflict_skips

    existing = {str(value) for value in row.get("hard_negative_for") or []}
    new_roles = derived - existing - positives
    row["hard_negative_for"] = sorted((existing | derived) - positives)
    row["candidate_targets"] = sorted(
        set(str(value) for value in row.get("candidate_targets") or [])
        | set(row["hard_negative_for"])
    )

    provenance = set(str(value) for value in row.get("label_provenance") or [])
    for source_positive, target in eligible_derivations:
        if target in positives:
            continue
        if not semantic.get(target):
            semantic[target] = CROSS_TARGET_SEMANTIC_STATUS
        provenance.add(f"{CROSS_TARGET_PROVENANCE_PREFIX}:{source_positive}->{target}")
    row["semantic_status_by_target"] = dict(sorted(semantic.items()))
    row["label_provenance"] = sorted(provenance)
    return len(new_roles), conflict_skips


def enrich_row(
    row: dict[str, Any],
    evidence: Mapping[str, Any] | None,
    source_policy: Mapping[str, Any],
    cross_target_mapping: Mapping[str, tuple[str, ...]],
) -> tuple[int, int]:
    blockers = {
        str(value) for value in row.get("blocking_reasons") or []
        if str(value) != DERIVED_FINGERPRINT_BLOCKER
    }
    row["blocking_reasons"] = sorted(blockers)

    if evidence:
        byte_size = evidence.get("byte_size")
        if byte_size is not None and int(byte_size or 0) > 0:
            existing = int(row.get("byte_size") or 0)
            if existing and existing != int(byte_size):
                blockers.add("IDENTITY_CONFLICT_BYTE_SIZE")
            else:
                row["byte_size"] = int(byte_size)
        probe = evidence.get("audio_probe")
        if isinstance(probe, Mapping):
            existing_probe = row.get("audio_probe")
            if isinstance(existing_probe, Mapping) and dict(existing_probe) != dict(probe):
                blockers.add("IDENTITY_CONFLICT_AUDIO_PROBE")
            else:
                row["audio_probe"] = dict(probe)
        fp = evidence.get("canonical_fingerprint")
        if isinstance(fp, Mapping) and fp.get("vector_sha256"):
            existing_fp = row.get("canonical_fingerprint")
            if isinstance(existing_fp, Mapping) and dict(existing_fp) != dict(fp):
                blockers.add("IDENTITY_CONFLICT_CANONICAL_FINGERPRINT")
            else:
                row["canonical_fingerprint"] = dict(fp)
        merge_semantic_hard_negatives(row, evidence)

    cross_target_roles, cross_target_conflict_skips = apply_cross_target_hard_negatives(
        row, cross_target_mapping
    )
    row["blocking_reasons"] = sorted(blockers)
    recompute_stage(row, source_policy)

    has_exact_role = bool(row.get("echo_labels") or row.get("hard_negative_for"))
    fp = row.get("canonical_fingerprint")
    if has_exact_role and not (isinstance(fp, Mapping) and fp.get("vector_sha256")):
        blockers = set(str(value) for value in row.get("blocking_reasons") or [])
        blockers.add(DERIVED_FINGERPRINT_BLOCKER)
        row["blocking_reasons"] = sorted(blockers)
        row["stage_status"] = "BLOCKED"
    return cross_target_roles, cross_target_conflict_skips


def main() -> int:
    required_paths = (
        LEDGER,
        SUMMARY,
        SOURCE_POLICY_PATH,
        HARD_NEGATIVE_MAPPING,
        SONYC_TARGETS,
        SONYC_CONFUSERS,
        FREESOUND,
        PUBLIC_GAP,
    )
    for path in required_paths:
        if not path.is_file():
            raise SystemExit(f"required evidence missing: {path.relative_to(ROOT)}")

    source_policy = load_dataset_certification(SOURCE_POLICY_PATH)
    cross_target_mapping = load_cross_target_confusers()
    index = technical_index()
    rows = read_jsonl(LEDGER)
    matched = 0
    cross_target_roles_attached = 0
    cross_target_semantic_conflict_skips = 0
    for row in rows:
        evidence = index.get(str(row["ledger_asset_id"]))
        if evidence:
            matched += 1
        attached, skipped = enrich_row(
            row,
            evidence,
            source_policy,
            cross_target_mapping,
        )
        cross_target_roles_attached += attached
        cross_target_semantic_conflict_skips += skipped

    rows = validate_ledger(rows)
    previous_summary = read_json(SUMMARY)
    summary = summarize_ledger(rows)
    summary.update({
        key: value
        for key, value in previous_summary.items()
        if key not in summary and key not in {"enrichment"}
    })
    summary["enrichment"] = {
        "status": "PASS",
        "matched_asset_count": matched,
        "technical_evidence_asset_count": len(index),
        "cross_target_hard_negative_roles_attached": cross_target_roles_attached,
        "cross_target_semantic_conflict_skips": cross_target_semantic_conflict_skips,
        "cross_target_mapping": {
            key: list(value) for key, value in sorted(cross_target_mapping.items())
        },
        "inputs": {
            str(path.relative_to(ROOT)): file_sha256(path)
            for path in (SONYC_TARGETS, SONYC_CONFUSERS, FREESOUND, PUBLIC_GAP, HARD_NEGATIVE_MAPPING)
        },
        "fingerprint_stop_line": "Every exact positive or hard-negative role requires a canonical fingerprint before global near-duplicate audit readiness.",
        "hard_negative_stop_line": "FSD50K source confusers and governed exact-positive cross-target confusers create hard-negative roles only; they never promote, remove or rewrite positive ECHO labels. Existing review/conflict semantics block cross-target credit for that destination."
    }

    with LEDGER.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "entries": summary["entry_count"],
        "matched": matched,
        "fingerprinted": summary["canonical_fingerprint_count"],
        "fingerprints_missing": summary["canonical_fingerprint_missing_count"],
        "cross_target_hard_negative_roles_attached": cross_target_roles_attached,
        "cross_target_semantic_conflict_skips": cross_target_semantic_conflict_skips,
        "hard_negative_counts": summary["hard_negative_counts"],
        "stage_status_counts": summary["stage_status_counts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
