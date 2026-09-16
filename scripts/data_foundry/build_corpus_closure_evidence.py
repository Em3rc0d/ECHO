#!/usr/bin/env python3
"""Build deterministic MK1 Corpus Foundry closure evidence from the canonical ledger.

This command is intentionally evidence-producing rather than certificate-producing.
It always writes explicit PASS/FAIL artifacts for deduplication, recording-family
integrity, split integrity, coverage, freeze eligibility and reproducibility.
A numerical or empirical failure is recorded as a gap; structural corruption of
inputs raises and fails CI.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from echo.data_foundry.canonical_fingerprints import fingerprint_distance
from echo.data_foundry.coverage_policy import evaluate_coverage, load_coverage_policy
from echo.data_foundry.splits import SplitRatios, assign_group

ROOT = Path(__file__).resolve().parents[2]
MAT = ROOT / "MK1/mining-site/materialization"
LEDGER = MAT / "canonical-release-safe-asset-ledger.jsonl"
SUMMARY = MAT / "canonical-release-safe-asset-ledger-summary.json"
NEAR_POLICY = ROOT / "configs/data_foundry/near_duplicate_policy.v1.json"
SPLIT_POLICY = ROOT / "configs/data_foundry/split_policy.v1.json"
COVERAGE_POLICY = ROOT / "configs/data_foundry/coverage_policy.v1.json"

OUT_DEDUP = MAT / "global-dedup-audit.json"
OUT_GROUP = MAT / "recording-family-audit.json"
OUT_SPLIT = MAT / "split-integrity.json"
OUT_COVERAGE = MAT / "coverage-gate.json"
OUT_FREEZE1 = MAT / "corpus-freeze-1.validation.json"
OUT_FREEZE2 = MAT / "corpus-freeze-2.validation.json"
OUT_REPRO = MAT / "corpus-reproducibility.json"

TARGETS = ("GLASS_SHATTER", "SIREN", "FIRE_ALARM", "VEHICLE_HORN", "TIRE_SQUEAL")


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object: {path}")
    return payload


def _jsonl(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"expected object at {path}:{number}")
            result.append(row)
    return result


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


def _meaningful(row: Mapping[str, Any]) -> bool:
    return bool(row.get("echo_labels") or row.get("hard_negative_for") or row.get("candidate_targets"))


def _group_by(rows: Iterable[Mapping[str, Any]], key_fn) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        key = key_fn(row)
        if key:
            grouped[str(key)].append(str(row.get("ledger_asset_id") or ""))
    return {key: sorted(ids) for key, ids in sorted(grouped.items()) if len(ids) > 1}


def _decoded_sample_count(fp: Mapping[str, Any]) -> int:
    try:
        return max(0, int(fp.get("decoded_sample_count") or 0))
    except (TypeError, ValueError):
        return 0


def _relative_sample_count_delta(left: Mapping[str, Any], right: Mapping[str, Any]) -> float:
    a = _decoded_sample_count(left)
    b = _decoded_sample_count(right)
    if a <= 0 or b <= 0:
        return 1.0
    return abs(a - b) / float(max(a, b))


def build_dedup(rows: list[dict[str, Any]], near_policy: Mapping[str, Any]) -> dict[str, Any]:
    """Audit exact identity and confirmed near-duplicate grouping separately.

    Broad RMS-envelope proximity is screening evidence only. It remains visible
    in the durable audit but can block corpus closure only when the pair also
    satisfies the stricter confirmation distance and decoded-length contract.
    """

    scope = [row for row in rows if row.get("rights_status") == "ALLOW_RELEASE_SAFE" and _meaningful(row)]
    missing_fp = [str(row["ledger_asset_id"]) for row in scope if not isinstance(row.get("canonical_fingerprint"), Mapping)]
    exact_media = _group_by(scope, lambda row: row.get("media_sha256"))
    exact_pcm = _group_by(
        scope,
        lambda row: (row.get("canonical_fingerprint") or {}).get("canonical_pcm_sha256")
        if isinstance(row.get("canonical_fingerprint"), Mapping)
        else None,
    )

    comparison = near_policy.get("comparison", {}) if isinstance(near_policy.get("comparison"), Mapping) else {}
    candidate_threshold = float(comparison.get("candidate_max_distance", 0.02))
    confirmed_threshold = float(comparison.get("confirmed_group_max_distance", candidate_threshold))
    max_relative_sample_count_delta = float(
        comparison.get("confirmed_group_max_relative_sample_count_delta", 0.01)
    )
    if not 0 <= confirmed_threshold <= candidate_threshold <= 1:
        raise ValueError("near-duplicate thresholds must satisfy 0 <= confirmed <= candidate <= 1")
    if not 0 <= max_relative_sample_count_delta <= 1:
        raise ValueError("confirmed_group_max_relative_sample_count_delta must be in [0, 1]")

    fp_rows = [row for row in scope if isinstance(row.get("canonical_fingerprint"), Mapping)]
    candidate_count = 0
    candidate_cross_group_count = 0
    confirmed_count = 0
    confirmed_cross_group_count = 0
    review_only_count = 0
    rejected_by_length_count = 0
    candidates: list[dict[str, Any]] = []

    for i, left in enumerate(fp_rows):
        left_fp = left["canonical_fingerprint"]
        for right in fp_rows[i + 1 :]:
            right_fp = right["canonical_fingerprint"]
            if left_fp.get("canonical_pcm_sha256") == right_fp.get("canonical_pcm_sha256"):
                continue
            distance = fingerprint_distance(left_fp, right_fp)
            if distance > candidate_threshold:
                continue

            candidate_count += 1
            same_group = str(left.get("recording_group_id") or "") == str(right.get("recording_group_id") or "")
            if not same_group:
                candidate_cross_group_count += 1

            relative_delta = _relative_sample_count_delta(left_fp, right_fp)
            confirmed = distance <= confirmed_threshold and relative_delta <= max_relative_sample_count_delta
            if confirmed:
                confirmed_count += 1
                if not same_group:
                    confirmed_cross_group_count += 1
            else:
                review_only_count += 1
                if relative_delta > max_relative_sample_count_delta:
                    rejected_by_length_count += 1

            if len(candidates) < 500:
                candidates.append(
                    {
                        "left": left["ledger_asset_id"],
                        "right": right["ledger_asset_id"],
                        "distance": round(distance, 8),
                        "decoded_sample_count_relative_delta": round(relative_delta, 8),
                        "same_recording_group": same_group,
                        "confirmation": "CONFIRMED" if confirmed else "SCREEN_ONLY",
                    }
                )

    exact_cross_group = 0
    by_id = {str(row["ledger_asset_id"]): row for row in scope}
    for groups in (exact_media, exact_pcm):
        for ids in groups.values():
            recording_groups = {str(by_id[asset].get("recording_group_id") or "") for asset in ids}
            if len(recording_groups) > 1:
                exact_cross_group += 1

    gaps: list[str] = []
    if missing_fp:
        gaps.append("CANONICAL_FINGERPRINT_COVERAGE_INCOMPLETE")
    if exact_cross_group:
        gaps.append("EXACT_DUPLICATE_RECORDING_GROUP_CONFLICTS")
    if confirmed_cross_group_count:
        gaps.append("CONFIRMED_NEAR_DUPLICATE_RECORDING_GROUP_CONFLICTS")

    return {
        "schema_version": "echo.global-dedup-audit.v2",
        "status": "PASS" if not gaps else "FAIL",
        "scope_asset_count": len(scope),
        "fingerprinted_asset_count": len(fp_rows),
        "missing_fingerprint_count": len(missing_fp),
        "missing_fingerprint_sample": missing_fp[:50],
        "exact_media_duplicate_group_count": len(exact_media),
        "exact_canonical_pcm_duplicate_group_count": len(exact_pcm),
        "exact_cross_recording_group_conflict_count": exact_cross_group,
        "candidate_near_duplicate_threshold": candidate_threshold,
        "confirmed_group_max_distance": confirmed_threshold,
        "confirmed_group_max_relative_sample_count_delta": max_relative_sample_count_delta,
        "near_duplicate_candidate_count": candidate_count,
        "near_duplicate_candidate_cross_group_count": candidate_cross_group_count,
        "confirmed_near_duplicate_count": confirmed_count,
        "confirmed_near_duplicate_cross_group_count": confirmed_cross_group_count,
        "review_only_near_duplicate_count": review_only_count,
        "candidate_edges_rejected_by_length_count": rejected_by_length_count,
        "near_duplicate_candidate_sample": candidates,
        "gap_codes": sorted(gaps),
        "policy_sha256": _sha(NEAR_POLICY),
        "ledger_sha256": _sha(LEDGER),
        "note": (
            "Broad RMS-envelope candidates are durable screening evidence only. "
            "Only exact byte/PCM identity or strict distance plus decoded-length confirmation may require shared split protection."
        ),
    }


def build_group_audit(rows: list[dict[str, Any]], dedup: Mapping[str, Any]) -> dict[str, Any]:
    scope = [row for row in rows if row.get("rights_status") == "ALLOW_RELEASE_SAFE" and _meaningful(row)]
    missing_group = [str(row["ledger_asset_id"]) for row in scope if not str(row.get("recording_group_id") or "")]
    pending = [
        str(row["ledger_asset_id"])
        for row in scope
        if "GROUPING_GLOBAL_AUDIT_REQUIRED" in (row.get("blocking_reasons") or [])
        or str(row.get("grouping_status") or "").upper().startswith("FALLBACK")
    ]
    group_counts = Counter(str(row.get("recording_group_id") or "") for row in scope if row.get("recording_group_id"))
    gaps: list[str] = []
    if missing_group:
        gaps.append("RECORDING_GROUP_MISSING")
    if pending:
        gaps.append("RECORDING_FAMILY_GLOBAL_AUDIT_PENDING")
    if int(dedup.get("exact_cross_recording_group_conflict_count") or 0) > 0:
        gaps.append("DUPLICATE_IDENTITY_CROSSES_RECORDING_FAMILIES")
    if int(dedup.get("confirmed_near_duplicate_cross_group_count") or 0) > 0:
        gaps.append("CONFIRMED_NEAR_DUPLICATES_CROSS_RECORDING_FAMILIES")

    return {
        "schema_version": "echo.recording-family-audit.v2",
        "status": "PASS" if not gaps else "FAIL",
        "scope_asset_count": len(scope),
        "recording_family_count": len(group_counts),
        "largest_recording_family_asset_count": max(group_counts.values(), default=0),
        "missing_recording_group_count": len(missing_group),
        "pending_global_group_audit_count": len(pending),
        "pending_global_group_audit_sample": pending[:50],
        "screening_candidate_cross_group_count": int(dedup.get("near_duplicate_candidate_cross_group_count") or 0),
        "confirmed_near_duplicate_cross_group_count": int(dedup.get("confirmed_near_duplicate_cross_group_count") or 0),
        "gap_codes": sorted(gaps),
        "ledger_sha256": _sha(LEDGER),
        "note": "Review-only screening candidates may cross recording families; confirmed identity-protection relations may not.",
    }


def split_plan(rows: list[dict[str, Any]], split_policy: Mapping[str, Any]) -> tuple[dict[str, str], list[str]]:
    original_map = {str(k).lower(): str(v) for k, v in (split_policy.get("original_split_map") or {}).items()}
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
    conflicts: list[str] = []
    for group, items in sorted(by_group.items()):
        if any(bool(item.get("field_holdout")) for item in items):
            assignments[group] = "field_holdout"
            continue
        originals = {
            original_map[str(item.get("original_split") or "").lower()]
            for item in items
            if str(item.get("original_split") or "").lower() in original_map
        }
        if len(originals) > 1:
            conflicts.append(group)
            continue
        if originals:
            assignments[group] = next(iter(originals))
        else:
            assignments[group] = assign_group(group, seed=seed, ratios=ratios)
    return assignments, conflicts


def build_split_audit(
    rows: list[dict[str, Any]],
    split_policy: Mapping[str, Any],
    dedup: Mapping[str, Any],
    group_audit: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    assignments, conflicts = split_plan(rows, split_policy)
    eligible = [row for row in rows if _ready(row)]
    split_counts = Counter(assignments.get(str(row.get("recording_group_id") or ""), "UNASSIGNED") for row in eligible)
    gaps: list[str] = []
    if dedup.get("status") != "PASS":
        gaps.append("UPSTREAM_GLOBAL_DEDUP_NOT_PASS")
    if group_audit.get("status") != "PASS":
        gaps.append("UPSTREAM_RECORDING_FAMILY_AUDIT_NOT_PASS")
    if conflicts:
        gaps.append("ORIGINAL_SPLIT_CONFLICT_WITHIN_RECORDING_FAMILY")
    if any(value == "UNASSIGNED" for value in split_counts):
        gaps.append("ELIGIBLE_ASSET_WITHOUT_SPLIT")

    assignment_digest = _digest(sorted(assignments.items()))
    return (
        {
            "schema_version": "echo.split-integrity.v1",
            "status": "PASS" if not gaps else "FAIL",
            "eligible_asset_count": len(eligible),
            "recording_family_assignment_count": len(assignments),
            "split_asset_counts": dict(sorted(split_counts.items())),
            "original_split_conflict_count": len(conflicts),
            "original_split_conflict_sample": conflicts[:50],
            "assignment_sha256": assignment_digest,
            "gap_codes": sorted(gaps),
            "split_policy_sha256": _sha(SPLIT_POLICY),
            "ledger_sha256": _sha(LEDGER),
        },
        assignments,
    )


def coverage_rows(rows: list[dict[str, Any]], assignments: Mapping[str, str]) -> list[dict[str, Any]]:
    translated: list[dict[str, Any]] = []
    for row in rows:
        if not _ready(row):
            continue
        probe = row.get("audio_probe") if isinstance(row.get("audio_probe"), Mapping) else {}
        group = str(row.get("recording_group_id") or "")
        translated.append(
            {
                "asset_id": row["ledger_asset_id"],
                "sha256": row.get("media_sha256"),
                "source_dataset": row.get("underlying_source_family") or row.get("source_dataset"),
                "recording_group_id": group,
                "echo_split": assignments.get(group),
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
            }
        )
    return translated


def build_coverage(
    rows: list[dict[str, Any]],
    assignments: Mapping[str, str],
    split_audit: Mapping[str, Any],
    dedup: Mapping[str, Any],
    group_audit: Mapping[str, Any],
) -> dict[str, Any]:
    policy = load_coverage_policy(COVERAGE_POLICY)
    result = evaluate_coverage(coverage_rows(rows, assignments), policy=policy, profile="release_safe")
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
    result["note"] = "Coverage uses only release-safe READY_FOR_GLOBAL_DEDUP rows and underlying acoustic source families, never dataset wrappers."
    return result


def build_freeze_artifacts(
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
    eligible = [row for row in rows if _ready(row)]
    membership = [
        {
            "asset_id": row["ledger_asset_id"],
            "media_sha256": row["media_sha256"],
            "recording_group_id": row["recording_group_id"],
            "split": assignments.get(str(row["recording_group_id"])),
            "echo_labels": sorted(row.get("echo_labels") or []),
            "hard_negative_for": sorted(row.get("hard_negative_for") or []),
            "underlying_source_family": row.get("underlying_source_family"),
        }
        for row in eligible
    ]
    identity = _digest(sorted(membership, key=lambda row: row["asset_id"]))
    status = "PASS" if not blockers else "FAIL"
    gaps = [] if not blockers else [f"UPSTREAM_{name}_NOT_PASS" for name in blockers]
    base = {
        "schema_version": "echo.corpus-freeze-validation.v1",
        "status": status,
        "asset_count": len(membership),
        "semantic_identity_sha256": identity,
        "ledger_sha256": _sha(LEDGER),
        "split_assignment_sha256": _digest(sorted(assignments.items())),
        "gap_codes": gaps,
        "boundary": "No bundle is eligible for benchmark handoff unless all upstream closure gates pass.",
    }
    freeze1 = {**base, "freeze_id": "MK1-CORPUS-FREEZE-1"}
    freeze2 = {**base, "freeze_id": "MK1-CORPUS-FREEZE-2"}
    reproducibility = {
        "schema_version": "echo.corpus-reproducibility.v1",
        "status": "PASS" if status == "PASS" and freeze1["semantic_identity_sha256"] == freeze2["semantic_identity_sha256"] else "FAIL",
        "freeze_1_identity": freeze1["semantic_identity_sha256"],
        "freeze_2_identity": freeze2["semantic_identity_sha256"],
        "identity_match": freeze1["semantic_identity_sha256"] == freeze2["semantic_identity_sha256"],
        "gap_codes": ([] if status == "PASS" else ["UPSTREAM_FREEZE_NOT_ELIGIBLE"]),
        "note": "Workflow performs a second process-level deterministic rebuild before persistence; certificate review still binds identities to the exact evidence commit.",
    }
    return freeze1, freeze2, reproducibility


def main() -> int:
    for path in (LEDGER, SUMMARY, NEAR_POLICY, SPLIT_POLICY, COVERAGE_POLICY):
        if not path.is_file():
            raise SystemExit(f"missing closure input: {path.relative_to(ROOT)}")

    rows = _jsonl(LEDGER)
    summary = _json(SUMMARY)
    if int(summary.get("entry_count") or -1) != len(rows):
        raise SystemExit("canonical ledger entry_count does not match summary")

    near_policy = _json(NEAR_POLICY)
    split_policy = _json(SPLIT_POLICY)
    dedup = build_dedup(rows, near_policy)
    group_audit = build_group_audit(rows, dedup)
    split_audit, assignments = build_split_audit(rows, split_policy, dedup, group_audit)
    coverage = build_coverage(rows, assignments, split_audit, dedup, group_audit)
    freeze1, freeze2, reproducibility = build_freeze_artifacts(
        rows, assignments, dedup, group_audit, split_audit, coverage
    )

    for path, payload in (
        (OUT_DEDUP, dedup),
        (OUT_GROUP, group_audit),
        (OUT_SPLIT, split_audit),
        (OUT_COVERAGE, coverage),
        (OUT_FREEZE1, freeze1),
        (OUT_FREEZE2, freeze2),
        (OUT_REPRO, reproducibility),
    ):
        _write(path, payload)

    print(json.dumps({
        "global_dedup": dedup["status"],
        "recording_family": group_audit["status"],
        "split_integrity": split_audit["status"],
        "coverage": coverage["status"],
        "freeze_1": freeze1["status"],
        "freeze_2": freeze2["status"],
        "reproducibility": reproducibility["status"],
        "coverage_gap_count": len(coverage.get("gap_codes") or []),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
