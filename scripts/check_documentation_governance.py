#!/usr/bin/env python3
"""Fail closed when ECHO documentation/certification truth drifts.

DOC-014 separates semantic corpus identity from execution provenance.
The corpus identity is bound to canonical ledger content, policy and closure evidence.
A commit used to execute a deterministic rebuild remains auditable provenance, but
must not masquerade as a data change when corpus bytes/semantics are unchanged.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROMISE = "Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial"
CURRENT_DOC_CERT = "CERT-DOC-014"
EXPECTED_MD_COUNT = 218
EXPECTED_LEDGER_SHA256 = "cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1"
EXPECTED_COVERAGE_LEDGER_SHA256 = "93be3dceee44df0dfc51ab38c078f1e1e6587ba91e4fbbc53c3b65065e58bfa8"
EXPECTED_POLICY_SHA256 = "bc45947df58b22608e3f0a1aec682105efa3b0b949e99251076639ff98a81d36"
EXPECTED_EVIDENCE_IDENTITY = "4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405"

EXPECTED_READINESS_GAPS = {
    "CORPUS_CERTIFICATE_NOT_CERTIFIED",
    "COVERAGE_GATE_GAP_CODES_NOT_EMPTY",
    "COVERAGE_GATE_NOT_PASS",
    "COVERAGE_GATE_STATUS_NOT_PASS",
    "FIRE_ALARM_ASSETS_19_LT_50",
    "FREEZE_1_VALIDATION_NOT_PASS",
    "FREEZE_2_VALIDATION_NOT_PASS",
    "REPRODUCIBILITY_NOT_PASS",
    "TIRE_SQUEAL_ASSETS_14_LT_50",
}
EXPECTED_COVERAGE_GAPS = {
    "FIRE_ALARM_ASSETS_BELOW_MIN",
    "FIRE_ALARM_GROUPS_BELOW_MIN",
    "FIRE_ALARM_TEST_ASSETS_BELOW_MIN",
    "FIRE_ALARM_TEST_GROUPS_BELOW_MIN",
    "FIRE_ALARM_TRAIN_ASSETS_BELOW_MIN",
    "FIRE_ALARM_VALIDATION_ASSETS_BELOW_MIN",
    "FIRE_ALARM_VALIDATION_GROUPS_BELOW_MIN",
    "GLASS_SHATTER_SOURCE_CONCENTRATION_TOO_HIGH",
    "TIRE_SQUEAL_ASSETS_BELOW_MIN",
    "TIRE_SQUEAL_GROUPS_BELOW_MIN",
    "TIRE_SQUEAL_TEST_ASSETS_BELOW_MIN",
    "TIRE_SQUEAL_TEST_GROUPS_BELOW_MIN",
    "TIRE_SQUEAL_TRAIN_ASSETS_BELOW_MIN",
    "TIRE_SQUEAL_TRAIN_GROUPS_BELOW_MIN",
    "TIRE_SQUEAL_VALIDATION_ASSETS_BELOW_MIN",
    "TIRE_SQUEAL_VALIDATION_GROUPS_BELOW_MIN",
}
EXPECTED_QUALITY = {
    "assets_with_unknown_license": 0,
    "assets_without_label_provenance": 0,
    "assets_without_positive_duration": 0,
    "assets_without_valid_audio_probe": 0,
    "exact_duplicate_groups": 0,
    "near_duplicate_groups": 0,
}

REQUIRED_FILES = {
    "charter": ROOT / "PROJECT-CHARTER.md",
    "state": ROOT / "CURRENT-STATE.md",
    "doc_standard": ROOT / "governance/DOCUMENTATION-STANDARD.md",
    "doc_coverage": ROOT / "governance/DOCUMENTATION-COVERAGE.md",
    "doc_audit": ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-16-CORPUS-PIPELINE-014.md",
    "cert_ledger": ROOT / "governance/CERTIFICATION-LEDGER.md",
    "free_tier": ROOT / "governance/FREE-TIER-BOUNDARY.md",
    "foundry_gates": ROOT / "MK1/build/data-foundry/FOUNDRY-GATES.md",
    "near_policy": ROOT / "configs/data_foundry/near_duplicate_policy.v1.json",
    "sonyc_cert": ROOT / "MK1/mining-site/materialization/sonyc-v2.3-materialization-certificate.json",
    "ledger_summary": ROOT / "MK1/mining-site/materialization/canonical-release-safe-asset-ledger-summary.json",
    "dedup": ROOT / "MK1/mining-site/materialization/global-dedup-audit.json",
    "group_audit": ROOT / "MK1/mining-site/materialization/recording-family-audit.json",
    "split": ROOT / "MK1/mining-site/materialization/split-integrity.json",
    "coverage": ROOT / "MK1/mining-site/materialization/coverage-gate.json",
    "readiness": ROOT / "MK1/mining-site/materialization/corpus-closure-readiness.json",
    "freeze1": ROOT / "MK1/mining-site/materialization/corpus-freeze-1.validation.json",
    "freeze2": ROOT / "MK1/mining-site/materialization/corpus-freeze-2.validation.json",
    "repro": ROOT / "MK1/mining-site/materialization/corpus-reproducibility.json",
}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(name: str) -> dict[str, Any]:
    payload = json.loads(REQUIRED_FILES[name].read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{name}: expected JSON object")
    return payload


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ledger_state(body: str, cert_id: str, state: str) -> bool:
    return re.search(
        rf"\|\s*{re.escape(cert_id)}\s*\|.*\|\s*{re.escape(state)}\s*\|", body
    ) is not None


def semantic_identity(readiness: dict[str, Any]) -> str:
    material = readiness.get("evidence_identity_material")
    if not isinstance(material, dict):
        return ""
    return hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def main() -> int:
    failures: list[str] = []
    for name, path in REQUIRED_FILES.items():
        require(path.is_file(), f"missing required authority: {name} -> {path.relative_to(ROOT)}", failures)
    if failures:
        print("DOCUMENTATION GOVERNANCE: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    json_names = {
        "near_policy", "sonyc_cert", "ledger_summary", "dedup", "group_audit",
        "split", "coverage", "readiness", "freeze1", "freeze2", "repro",
    }
    docs = {name: text(path) for name, path in REQUIRED_FILES.items() if name not in json_names}
    near_policy = load_json("near_policy")
    sonyc = load_json("sonyc_cert")
    ledger = load_json("ledger_summary")
    dedup = load_json("dedup")
    group_audit = load_json("group_audit")
    split = load_json("split")
    coverage = load_json("coverage")
    readiness = load_json("readiness")
    freeze1 = load_json("freeze1")
    freeze2 = load_json("freeze2")
    repro = load_json("repro")

    # Immutable/project-wide ancestors.
    require(PROMISE in docs["charter"], "immutable promise missing from charter", failures)
    require(PROMISE in docs["state"], "immutable promise missing from CURRENT-STATE", failures)
    require("FROZEN_DOCUMENTATION_GOVERNANCE" in docs["doc_standard"], "documentation governance is not frozen", failures)
    require("ECHO-FREE-TIER-001" in docs["doc_standard"], "documentation standard lost free-tier ancestor", failures)
    require("FROZEN_GLOBAL_POLICY" in docs["free_tier"] and "0 USD" in docs["free_tier"], "free-tier invariant drift", failures)

    # Documentation/certificate lineage.
    require(CURRENT_DOC_CERT in docs["doc_coverage"] and "Current certificate" in docs["doc_coverage"], "DOCUMENTATION-COVERAGE does not name DOC-014 current", failures)
    require("CERT-DOC-014                   = CERTIFIED / current" in docs["state"], "CURRENT-STATE does not mark DOC-014 current", failures)
    require("**Certificate:** `CERT-DOC-014`" in docs["doc_audit"] and "**Status:** `CERTIFIED`" in docs["doc_audit"], "DOC-014 audit is not certified", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-014", "CERTIFIED"), "CERT-DOC-014 not CERTIFIED in certification ledger", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-001..013", "INVALIDATED"), "historical DOC certificates not invalidated through DOC-013", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-TOOLCHAIN-004", "INVALIDATED"), "TOOLCHAIN-004 must remain invalidated", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-TOOLCHAIN-005", "CANDIDATE"), "TOOLCHAIN-005 must remain candidate", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-SONYC-001", "CERTIFIED"), "SONYC certificate missing/not certified", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-CORPUS-001", "OPEN"), "corpus certificate must remain OPEN", failures)
    require("CERT-MK1-DF-TOOLCHAIN-005 = CANDIDATE" in docs["foundry_gates"], "FOUNDRY-GATES lost TOOLCHAIN-005 candidate state", failures)

    # Scoped SONYC certificate stays pinned.
    require(sonyc.get("artifact_id") == "CERT-MK1-DF-SONYC-001", "SONYC certificate id drift", failures)
    require(sonyc.get("status") == "CERTIFIED", "SONYC certificate status drift", failures)
    require(sonyc.get("implementation_baseline") == "ab8c47ba6aabb25390644954a2a06945ca7a81bb", "SONYC implementation baseline drift", failures)
    require(sonyc.get("materialization_run_id") == 34922010537, "SONYC materialization run drift", failures)
    require(sonyc.get("durable_evidence_commit") == "78fc019839f1c9dad1a58a70d439605d887361d7", "SONYC durable evidence drift", failures)
    ss = sonyc.get("materialization_summary") or {}
    require(ss.get("shards_expected") == 19 and ss.get("shards_materialized") == 19, "SONYC shard closure drift", failures)
    require(ss.get("probe_failures") == 0 and ss.get("fingerprint_failures") == 0, "SONYC technical failures reappeared", failures)
    require((sonyc.get("free_tier_boundary") or {}).get("result") == "PASS", "SONYC free-tier result drift", failures)

    # Near-duplicate semantics remain screen -> confirm -> group.
    comparison = near_policy.get("comparison") or {}
    require(float(comparison.get("candidate_max_distance", -1)) == 0.02, "candidate screening threshold drift", failures)
    require(float(comparison.get("confirmed_group_max_distance", -1)) == 0.002, "confirmed grouping threshold drift", failures)
    require(float(comparison.get("confirmed_group_max_relative_sample_count_delta", -1)) == 0.01, "confirmed sample-count compatibility drift", failures)
    require(comparison.get("automatic_merge") is False, "near-duplicate automatic merge must remain false", failures)
    require(comparison.get("action") == "SCREEN_THEN_CONFIRM_FOR_SPLIT_PROTECTION", "screen/confirm action drift", failures)
    require("review-only screening edges never union components" in str(comparison.get("transitive_rule") or ""), "transitive screening stop-line drift", failures)

    # Canonical corpus semantic truth. baseline_commit is provenance, not identity.
    baseline = str(ledger.get("baseline_commit") or "")
    require(re.fullmatch(r"[0-9a-f]{40}", baseline) is not None, "canonical ledger provenance baseline is not a commit SHA", failures)
    require(ledger.get("entry_count") == 1141, "canonical ledger entry count drift", failures)
    require(ledger.get("ledger_sha256") == EXPECTED_LEDGER_SHA256, "canonical semantic ledger identity drift", failures)
    require(ledger.get("canonical_fingerprint_count") == 1141, "canonical fingerprint count drift", failures)
    require(ledger.get("canonical_fingerprint_missing_count") == 0, "canonical fingerprints are missing", failures)
    require((ledger.get("blocking_reason_counts") or {}) == {}, "corpus-facing ledger blockers reappeared", failures)
    grouping = ledger.get("global_recording_group_resolution") or {}
    require(grouping.get("schema_version") == "echo.global-recording-group-resolution.v2", "global grouping schema drift", failures)
    require(grouping.get("status") == "PASS", "global recording-group resolution not PASS", failures)
    require(grouping.get("fallback_asset_count_after") == 0, "fallback grouping closure regressed", failures)
    require(grouping.get("global_acoustic_component_count") == 2, "global acoustic component count drift", failures)
    require(grouping.get("members_reassigned_to_global_acoustic_component") == 4, "global component membership drift", failures)
    require(grouping.get("near_duplicate_candidate_edge_count") == 855, "global candidate-edge count drift", failures)
    require(grouping.get("confirmed_near_duplicate_grouping_edge_count") == 2, "confirmed grouping-edge count drift", failures)
    require(grouping.get("review_only_near_duplicate_edge_count") == 853, "review-only edge count drift", failures)
    require(grouping.get("candidate_edges_rejected_by_length_count") == 835, "length-rejected edge count drift", failures)
    require(grouping.get("content_deleted") is False and grouping.get("content_merge_performed") is False, "grouping must not delete/merge content", failures)
    require(ledger.get("positive_counts") == {"FIRE_ALARM": 19, "GLASS_SHATTER": 303, "SIREN": 169, "TIRE_SQUEAL": 14, "VEHICLE_HORN": 235}, "ledger positive counts drift", failures)
    require(ledger.get("hard_negative_counts") == {"FIRE_ALARM": 202, "GLASS_SHATTER": 440, "SIREN": 235, "TIRE_SQUEAL": 25, "VEHICLE_HORN": 142}, "ledger hard-negative counts drift", failures)
    require(ledger.get("hard_negative_underlying_source_family_counts") == {"FIRE_ALARM": 4, "GLASS_SHATTER": 2, "SIREN": 4, "TIRE_SQUEAL": 2, "VEHICLE_HORN": 3}, "hard-negative source-family counts drift", failures)

    # Structural closure remains green.
    require(dedup.get("schema_version") == "echo.global-dedup-audit.v2", "global dedup schema drift", failures)
    require(dedup.get("status") == "PASS" and dedup.get("gap_codes") == [], "global dedup must remain PASS", failures)
    require(dedup.get("ledger_sha256") == EXPECTED_COVERAGE_LEDGER_SHA256, "dedup material-ledger identity drift", failures)
    require(dedup.get("fingerprinted_asset_count") == 1141 and dedup.get("missing_fingerprint_count") == 0, "global dedup fingerprint coverage drift", failures)
    require(dedup.get("near_duplicate_candidate_count") == 855, "dedup screening candidate count drift", failures)
    require(dedup.get("near_duplicate_candidate_cross_group_count") == 849, "dedup cross-group screening count drift", failures)
    require(dedup.get("confirmed_near_duplicate_count") == 2, "dedup confirmed count drift", failures)
    require(dedup.get("confirmed_near_duplicate_cross_group_count") == 0, "confirmed near-duplicate cross-group conflict reappeared", failures)
    require(dedup.get("candidate_edges_rejected_by_length_count") == 835, "dedup length-rejected count drift", failures)
    require(dedup.get("exact_cross_recording_group_conflict_count") == 0, "exact duplicate identity crosses groups", failures)
    require(dedup.get("exact_media_duplicate_group_count") == 0 and dedup.get("exact_canonical_pcm_duplicate_group_count") == 0, "exact duplicate groups reappeared", failures)

    require(group_audit.get("schema_version") == "echo.recording-family-audit.v2", "recording-family audit schema drift", failures)
    require(group_audit.get("status") == "PASS" and group_audit.get("gap_codes") == [], "recording-family audit must remain PASS", failures)
    require(group_audit.get("recording_family_count") == 1075, "recording-family count drift", failures)
    require(group_audit.get("missing_recording_group_count") == 0 and group_audit.get("pending_global_group_audit_count") == 0, "recording-family unresolved state reappeared", failures)
    require(group_audit.get("confirmed_near_duplicate_cross_group_count") == 0, "recording-family confirmed conflict reappeared", failures)

    require(split.get("status") == "PASS" and split.get("gap_codes") == [], "split integrity must remain PASS", failures)
    require(split.get("original_split_conflict_count") == 0, "protected split conflict reappeared", failures)
    require(split.get("original_split_conflicts_quarantined") == 0, "unexpected protected split quarantine", failures)
    require(split.get("quarantined_asset_count") == 0 and split.get("quarantined_recording_family_count") == 0, "split quarantine drift", failures)
    require(split.get("eligible_asset_count") == 1141 and split.get("ready_candidate_asset_count") == 1141, "split eligible asset count drift", failures)
    require(split.get("split_asset_counts") == {"test": 463, "train": 439, "validation": 239}, "global split counts drift", failures)

    # Coverage truth remains empirical and exact.
    require(coverage.get("status") == "FAIL", "coverage status changed; fresh audit required", failures)
    require(coverage.get("ledger_sha256") == EXPECTED_COVERAGE_LEDGER_SHA256, "coverage ledger identity drift", failures)
    require(set(coverage.get("gap_codes") or []) == EXPECTED_COVERAGE_GAPS, "coverage detailed gap set drift", failures)
    require(len(coverage.get("gap_codes") or []) == 16, "coverage gap count must be exactly 16", failures)
    require(coverage.get("quarantined_split_conflict_asset_count") == 0, "coverage quarantine count drift", failures)
    require(coverage.get("development_asset_count") == 1141, "development asset count drift", failures)
    require((coverage.get("asset_quality") or {}) == EXPECTED_QUALITY, "asset-quality stop lines drift", failures)
    background = coverage.get("background") or {}
    require((background.get("asset_count"), background.get("independent_group_count"), background.get("source_count")) == (428, 385, 4), "background closure drift", failures)

    classes = coverage.get("classes") or {}
    fire = classes.get("FIRE_ALARM") or {}
    require((fire.get("asset_count"), fire.get("independent_group_count"), fire.get("source_count")) == (19, 16, 3), "FIRE final coverage drift", failures)
    require(fire.get("source_asset_counts") == {"BIGSOUNDBANK": 4, "FREESOUND": 12, "WIKIMEDIA_COMMONS": 3}, "FIRE source counts drift", failures)
    require(fire.get("split_assets") == {"test": 0, "train": 17, "validation": 2}, "FIRE split assets drift", failures)
    require(fire.get("split_groups") == {"test": 0, "train": 14, "validation": 2}, "FIRE split groups drift", failures)
    require(abs(float(fire.get("clip_duration_seconds") or 0.0) - 460.864037) < 1e-6, "FIRE duration drift", failures)
    fire_hn = fire.get("hard_negatives") or {}
    require((fire_hn.get("asset_count"), fire_hn.get("independent_group_count"), fire_hn.get("source_count")) == (202, 202, 4), "FIRE hard-negative closure drift", failures)

    glass = classes.get("GLASS_SHATTER") or {}
    require((glass.get("asset_count"), glass.get("independent_group_count"), glass.get("source_count")) == (303, 287, 4), "GLASS final coverage drift", failures)
    require(glass.get("source_asset_counts") == {"BIGSOUNDBANK": 16, "FREESOUND": 280, "OPENGAMEART_RUBBERDUCK": 6, "OPENGAMEART_TILL_BEHREND": 1}, "GLASS source counts drift", failures)
    require(glass.get("max_single_source_fraction") == 0.924092, "GLASS concentration drift", failures)
    require(abs(float(glass.get("clip_duration_seconds") or 0.0) - 1244.131193) < 1e-6, "GLASS duration drift", failures)
    glass_hn = glass.get("hard_negatives") or {}
    require((glass_hn.get("asset_count"), glass_hn.get("independent_group_count"), glass_hn.get("source_count")) == (440, 410, 2), "GLASS hard-negative closure drift", failures)

    tire = classes.get("TIRE_SQUEAL") or {}
    require((tire.get("asset_count"), tire.get("independent_group_count"), tire.get("source_count")) == (14, 10, 2), "TIRE final coverage drift", failures)
    require(tire.get("source_asset_counts") == {"BIGSOUNDBANK": 5, "FREESOUND": 9}, "TIRE source counts drift", failures)
    require(tire.get("split_assets") == {"test": 3, "train": 11, "validation": 0}, "TIRE split assets drift", failures)
    require(tire.get("split_groups") == {"test": 2, "train": 8, "validation": 0}, "TIRE split groups drift", failures)
    require(abs(float(tire.get("clip_duration_seconds") or 0.0) - 344.600098) < 1e-6, "TIRE duration drift", failures)
    tire_hn = tire.get("hard_negatives") or {}
    require((tire_hn.get("asset_count"), tire_hn.get("independent_group_count"), tire_hn.get("source_count")) == (25, 12, 2), "TIRE hard-negative closure drift", failures)

    siren = classes.get("SIREN") or {}
    horn = classes.get("VEHICLE_HORN") or {}
    require((siren.get("asset_count"), siren.get("independent_group_count")) == (169, 169), "SIREN closure drift", failures)
    require((horn.get("asset_count"), horn.get("independent_group_count")) == (235, 235), "VEHICLE_HORN closure drift", failures)

    # Freeze and reproducibility are blocked only by empirical coverage.
    require(freeze1.get("status") == "FAIL" and freeze1.get("gap_codes") == ["UPSTREAM_COVERAGE_NOT_PASS"], "freeze #1 gate drift", failures)
    require(freeze2.get("status") == "FAIL" and freeze2.get("gap_codes") == ["UPSTREAM_COVERAGE_NOT_PASS"], "freeze #2 gate drift", failures)
    require(repro.get("status") == "FAIL" and repro.get("gap_codes") == ["UPSTREAM_FREEZE_NOT_ELIGIBLE"], "reproducibility gate drift", failures)

    # Readiness v2 binds semantic identity, while provenance remains internally consistent.
    require(readiness.get("schema_version") == "echo.corpus-closure-readiness.v2", "readiness v2 not active", failures)
    require(readiness.get("readiness_id") == "EMP-MK1-CORPUS-READINESS-001", "readiness id drift", failures)
    require(readiness.get("status") == "BLOCKED", "readiness must remain BLOCKED", failures)
    require(set(readiness.get("gap_codes") or []) == EXPECTED_READINESS_GAPS, "readiness gap set drift", failures)
    require(readiness.get("eligible_for_certificate_review") is False, "readiness unexpectedly eligible for certificate review", failures)
    require(readiness.get("modeling_allowed") is False, "modeling must remain locked", failures)
    require(readiness.get("next_authorized_stage") == "CORPUS_FOUNDRY_CLOSURE", "next authorized stage drift", failures)
    require((readiness.get("corpus_certificate") or {}).get("status") == "OPEN", "readiness corpus certificate state drift", failures)

    ri = (readiness.get("inputs") or {}).get("canonical_ledger_summary") or {}
    require(ri.get("baseline_commit") == baseline, "readiness provenance baseline disagrees with canonical ledger summary", failures)
    require(ri.get("entry_count") == 1141, "readiness ledger entry count drift", failures)
    require(ri.get("ledger_sha256") == EXPECTED_LEDGER_SHA256, "readiness semantic ledger binding drift", failures)
    require(re.fullmatch(r"[0-9a-f]{64}", str(ri.get("sha256") or "")) is not None, "readiness summary provenance hash invalid", failures)
    require("execution provenance" in str(ri.get("provenance_note") or ""), "readiness lost semantic/provenance boundary note", failures)

    material = readiness.get("evidence_identity_material") or {}
    require(material.get("canonical_ledger_semantic_sha256") == EXPECTED_LEDGER_SHA256, "readiness identity does not bind canonical semantic ledger", failures)
    require(material.get("coverage_policy_sha256") == EXPECTED_POLICY_SHA256, "readiness policy identity drift", failures)
    closure_hashes = material.get("closure_evidence_sha256") or {}
    for node, item in (readiness.get("closure_evidence_nodes") or {}).items():
        require(closure_hashes.get(node) == item.get("sha256"), f"readiness identity material/hash mismatch: {node}", failures)
    computed_identity = semantic_identity(readiness)
    require(readiness.get("evidence_identity_sha256") == computed_identity, "readiness semantic identity is not self-consistent", failures)
    require(computed_identity == EXPECTED_EVIDENCE_IDENTITY, "readiness semantic identity drift", failures)

    targets = readiness.get("target_readiness") or {}
    require((targets.get("FIRE_ALARM") or {}).get("positive_assets_pre_final_dedup") == 19, "readiness FIRE count drift", failures)
    require((targets.get("TIRE_SQUEAL") or {}).get("positive_assets_pre_final_dedup") == 14, "readiness TIRE count drift", failures)
    require((targets.get("GLASS_SHATTER") or {}).get("positive_assets_pre_final_dedup") == 303, "readiness GLASS count drift", failures)

    # Current documentation must describe the semantic/provenance boundary and release stop line.
    for name in ("state", "doc_coverage", "cert_ledger", "doc_audit"):
        body = docs[name]
        require("CERT-MK1-DF-CORPUS-001" in body, f"{name} lost corpus certificate stop line", failures)
        require("Benchmark A/B/C" in body, f"{name} lost benchmark gate", failures)
        require(EXPECTED_LEDGER_SHA256 in body, f"{name} lost canonical semantic ledger identity", failures)
        require("execution provenance" in body.lower(), f"{name} lost semantic/provenance boundary", failures)
    require("modeling_allowed = false" in docs["state"], "CURRENT-STATE lost modeling lock", failures)

    markdown_files = sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)
    require(len(markdown_files) == EXPECTED_MD_COUNT, f"Markdown corpus count drift: expected {EXPECTED_MD_COUNT}, got {len(markdown_files)}", failures)
    for path in markdown_files:
        body = text(path)
        if "<<<<<<< " in body or "\n>>>>>>> " in body:
            failures.append(f"merge-conflict marker detected in {path.relative_to(ROOT)}")

    if failures:
        print("DOCUMENTATION GOVERNANCE: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    print("DOCUMENTATION GOVERNANCE: PASS")
    print(f" certificate={CURRENT_DOC_CERT} markdown_files={len(markdown_files)}")
    print(f" semantic_ledger={EXPECTED_LEDGER_SHA256}")
    print(f" readiness_identity={computed_identity}")
    print(f" execution_baseline={baseline} (provenance only)")
    print(" dedup=PASS family=PASS split=PASS quarantine=0")
    print(f" ledger_entries=1141 coverage_gaps={len(EXPECTED_COVERAGE_GAPS)} modeling_allowed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
