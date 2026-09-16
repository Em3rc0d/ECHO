#!/usr/bin/env python3
"""Fail closed when ECHO documentation/certification truth drifts."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PROMISE = "Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial"
EXPECTED_MD_COUNT = 216
EXPECTED_READINESS_COMMIT = "48af9f220b30f2197aa376bff025195cb0a2a13b"
EXPECTED_EVIDENCE_IDENTITY = "85dee5596dbc9c88e0430e32b5e8eec7c014d526d132974542b2e4a36a108a50"
EXPECTED_LEDGER_BASELINE = "050f2ebc39fea0d1e6903190ad471fd97d1487dc"
EXPECTED_LEDGER_SHA256 = "1ab3712452f42205fe9004f1d6cb9e778297487891bb373e5c42d635854f1d85"
EXPECTED_COVERAGE_LEDGER_SHA256 = "72039f7f11b08fcadbe19ee1cf639f929491a67f59bce36d3ee953f366364f14"
EXPECTED_GAPS = {
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

REQUIRED_FILES = {
    "charter": ROOT / "PROJECT-CHARTER.md",
    "state": ROOT / "CURRENT-STATE.md",
    "doc_standard": ROOT / "governance/DOCUMENTATION-STANDARD.md",
    "doc_coverage": ROOT / "governance/DOCUMENTATION-COVERAGE.md",
    "doc_audit": ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-16-CORPUS-CLOSURE-012.md",
    "cert_ledger": ROOT / "governance/CERTIFICATION-LEDGER.md",
    "free_tier": ROOT / "governance/FREE-TIER-BOUNDARY.md",
    "foundry_gates": ROOT / "MK1/build/data-foundry/FOUNDRY-GATES.md",
    "sonyc_cert": ROOT / "MK1/mining-site/materialization/sonyc-v2.3-materialization-certificate.json",
    "ledger_summary": ROOT / "MK1/mining-site/materialization/canonical-release-safe-asset-ledger-summary.json",
    "dedup": ROOT / "MK1/mining-site/materialization/global-dedup-audit.json",
    "group_audit": ROOT / "MK1/mining-site/materialization/recording-family-audit.json",
    "split": ROOT / "MK1/mining-site/materialization/split-integrity.json",
    "coverage": ROOT / "MK1/mining-site/materialization/coverage-gate.json",
    "readiness": ROOT / "MK1/mining-site/materialization/corpus-closure-readiness.json",
    "near_policy": ROOT / "configs/data_foundry/near_duplicate_policy.v1.json",
}


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(name: str) -> dict:
    return json.loads(REQUIRED_FILES[name].read_text(encoding="utf-8"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def ledger_state(body: str, cert_id: str, state: str) -> bool:
    return re.search(rf"\|\s*{re.escape(cert_id)}\s*\|.*\|\s*{re.escape(state)}\s*\|", body) is not None


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
        "readiness", "sonyc_cert", "ledger_summary", "dedup", "group_audit",
        "split", "coverage", "near_policy",
    }
    docs = {name: text(path) for name, path in REQUIRED_FILES.items() if name not in json_names}
    readiness = load_json("readiness")
    sonyc = load_json("sonyc_cert")
    ledger = load_json("ledger_summary")
    dedup = load_json("dedup")
    group_audit = load_json("group_audit")
    split = load_json("split")
    coverage = load_json("coverage")
    near_policy = load_json("near_policy")

    # Immutable product and zero-cost ancestors.
    require(PROMISE in docs["charter"], "immutable promise missing from charter", failures)
    require(PROMISE in docs["state"], "immutable promise missing from current state", failures)
    require("FROZEN_DOCUMENTATION_GOVERNANCE" in docs["doc_standard"], "documentation governance not frozen", failures)
    require("ECHO-FREE-TIER-001" in docs["doc_standard"], "documentation standard lacks free-tier ancestor", failures)
    require("FROZEN_GLOBAL_POLICY" in docs["free_tier"] and "0 USD" in docs["free_tier"], "zero-cost boundary drift", failures)

    # Documentation and certification lineage.
    require("CERT-DOC-012" in docs["doc_coverage"] and "Current certificate" in docs["doc_coverage"], "DOCUMENTATION-COVERAGE does not name DOC-012 current", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-012", "CERTIFIED"), "CERT-DOC-012 not certified in ledger", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-001..011", "INVALIDATED"), "historical DOC certificates not invalidated", failures)
    require("CERT-DOC-012" in docs["state"] and "CERTIFIED / current" in docs["state"], "CURRENT-STATE does not show DOC-012 current", failures)
    require("**Certificate:** `CERT-DOC-012`" in docs["doc_audit"] and "**Status:** `CERTIFIED`" in docs["doc_audit"], "DOC-012 audit not certified", failures)
    require(EXPECTED_READINESS_COMMIT in docs["doc_audit"], "DOC-012 missing audited readiness commit", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-TOOLCHAIN-004", "INVALIDATED"), "toolchain-004 must remain invalidated", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-TOOLCHAIN-005", "CANDIDATE"), "toolchain-005 must remain candidate", failures)
    require("CERT-MK1-DF-TOOLCHAIN-005 = CANDIDATE" in docs["foundry_gates"], "FOUNDRY-GATES missing toolchain-005 candidate", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-SONYC-001", "CERTIFIED"), "SONYC certificate missing/not certified", failures)

    # Scoped SONYC certificate remains exact.
    require(sonyc.get("artifact_id") == "CERT-MK1-DF-SONYC-001" and sonyc.get("status") == "CERTIFIED", "SONYC certificate drift", failures)
    require(sonyc.get("implementation_baseline") == "ab8c47ba6aabb25390644954a2a06945ca7a81bb", "SONYC baseline drift", failures)
    require(sonyc.get("materialization_run_id") == 34922010537, "SONYC run drift", failures)
    require(sonyc.get("durable_evidence_commit") == "78fc019839f1c9dad1a58a70d439605d887361d7", "SONYC durable evidence drift", failures)
    ss = sonyc.get("materialization_summary", {})
    require(ss.get("shards_expected") == 19 and ss.get("shards_materialized") == 19, "SONYC shard closure drift", failures)
    require(ss.get("probe_failures") == 0 and ss.get("fingerprint_failures") == 0, "SONYC technical failures reappeared", failures)
    require(sonyc.get("free_tier_boundary", {}).get("result") == "PASS", "SONYC free-tier result drift", failures)

    # Current post-Freesound durable ledger.
    require(ledger.get("baseline_commit") == EXPECTED_LEDGER_BASELINE, "canonical ledger baseline drift", failures)
    require(ledger.get("entry_count") == 1141, "canonical ledger entry count drift", failures)
    require(ledger.get("ledger_sha256") == EXPECTED_LEDGER_SHA256, "canonical ledger identity drift", failures)
    require(ledger.get("canonical_fingerprint_count") == 1141 and ledger.get("canonical_fingerprint_missing_count") == 0, "canonical fingerprint closure drift", failures)
    require((ledger.get("blocking_reason_counts") or {}) == {}, "corpus-facing ledger blockers reappeared", failures)
    grouping = ledger.get("global_recording_group_resolution") or {}
    require(grouping.get("status") == "PASS", "global grouping not PASS", failures)
    require(grouping.get("fallback_asset_count_after") == 0, "fallback grouping closure regressed", failures)
    require(grouping.get("global_acoustic_component_count") == 12, "global acoustic component count drift", failures)
    require(grouping.get("members_reassigned_to_global_acoustic_component") == 118, "global component membership drift", failures)
    require(grouping.get("content_deleted") is False and grouping.get("content_merge_performed") is False, "grouping must not merge/delete content", failures)
    expected_positive = {"FIRE_ALARM": 19, "GLASS_SHATTER": 303, "SIREN": 169, "TIRE_SQUEAL": 14, "VEHICLE_HORN": 235}
    expected_hn = {"FIRE_ALARM": 202, "GLASS_SHATTER": 440, "SIREN": 235, "TIRE_SQUEAL": 25, "VEHICLE_HORN": 142}
    expected_hn_sources = {"FIRE_ALARM": 4, "GLASS_SHATTER": 2, "SIREN": 4, "TIRE_SQUEAL": 2, "VEHICLE_HORN": 3}
    require(ledger.get("positive_counts") == expected_positive, "positive corpus counts drift", failures)
    require(ledger.get("hard_negative_counts") == expected_hn, "hard-negative counts drift", failures)
    require(ledger.get("hard_negative_underlying_source_family_counts") == expected_hn_sources, "hard-negative source-family counts drift", failures)

    # Structural nodes remain closed on the audited durable baseline.
    require(dedup.get("status") == "PASS" and dedup.get("gap_codes") == [], "global dedup must remain PASS", failures)
    require(group_audit.get("status") == "PASS" and group_audit.get("gap_codes") == [], "recording-family audit must remain PASS", failures)
    require(split.get("status") == "PASS" and split.get("gap_codes") == [], "split integrity must remain PASS", failures)
    require(split.get("original_split_conflict_count") == 2, "split conflict count drift", failures)
    require(split.get("original_split_conflicts_quarantined") == 2, "all protected split conflicts must stay quarantined", failures)
    require(split.get("quarantined_asset_count") == 93, "quarantined asset count drift", failures)
    require(split.get("eligible_asset_count") == 1048, "eligible split asset count drift", failures)

    # Final coverage truth.
    require(coverage.get("status") == "FAIL", "coverage unexpectedly not FAIL; re-audit required", failures)
    require(coverage.get("ledger_sha256") == EXPECTED_COVERAGE_LEDGER_SHA256, "coverage ledger identity drift", failures)
    require(set(coverage.get("gap_codes", [])) == EXPECTED_COVERAGE_GAPS, "coverage gap-code set drift; re-audit required", failures)
    require(coverage.get("quarantined_split_conflict_asset_count") == 93, "coverage quarantine count drift", failures)
    background = coverage.get("background") or {}
    require((background.get("asset_count"), background.get("independent_group_count"), background.get("source_count")) == (416, 383, 4), "background closure drift", failures)
    classes = coverage.get("classes") or {}

    fire = classes.get("FIRE_ALARM") or {}
    require((fire.get("asset_count"), fire.get("independent_group_count"), fire.get("source_count")) == (19, 16, 3), "FIRE final coverage drift", failures)
    require(fire.get("split_assets") == {"test": 0, "train": 17, "validation": 2}, "FIRE split asset drift", failures)
    require(fire.get("split_groups") == {"test": 0, "train": 14, "validation": 2}, "FIRE split group drift", failures)
    require(fire.get("source_asset_counts") == {"BIGSOUNDBANK": 4, "FREESOUND": 12, "WIKIMEDIA_COMMONS": 3}, "FIRE source counts drift", failures)
    require(abs(float(fire.get("clip_duration_seconds") or 0.0) - 460.864037) < 1e-6, "FIRE duration drift", failures)
    fire_hn = fire.get("hard_negatives") or {}
    require((fire_hn.get("asset_count"), fire_hn.get("independent_group_count"), fire_hn.get("source_count")) == (202, 202, 4), "FIRE HN closure drift", failures)

    glass = classes.get("GLASS_SHATTER") or {}
    require((glass.get("asset_count"), glass.get("independent_group_count"), glass.get("source_count")) == (222, 205, 4), "GLASS final coverage drift", failures)
    require(glass.get("max_single_source_fraction") == 0.941441, "GLASS concentration drift", failures)
    require(glass.get("source_asset_counts") == {"BIGSOUNDBANK": 6, "FREESOUND": 209, "OPENGAMEART_RUBBERDUCK": 6, "OPENGAMEART_TILL_BEHREND": 1}, "GLASS source counts drift", failures)

    siren = classes.get("SIREN") or {}
    require((siren.get("asset_count"), siren.get("independent_group_count")) == (169, 169), "SIREN positive closure drift", failures)

    tire = classes.get("TIRE_SQUEAL") or {}
    require((tire.get("asset_count"), tire.get("independent_group_count"), tire.get("source_count")) == (14, 10, 2), "TIRE positive closure drift", failures)
    require(tire.get("split_assets") == {"test": 3, "train": 11, "validation": 0}, "TIRE split asset drift", failures)
    require(tire.get("split_groups") == {"test": 2, "train": 8, "validation": 0}, "TIRE split group drift", failures)
    tire_hn = tire.get("hard_negatives") or {}
    require((tire_hn.get("asset_count"), tire_hn.get("independent_group_count"), tire_hn.get("source_count")) == (25, 12, 2), "TIRE hard-negative closure drift", failures)

    horn = classes.get("VEHICLE_HORN") or {}
    require((horn.get("asset_count"), horn.get("independent_group_count")) == (235, 235), "VEHICLE_HORN positive closure drift", failures)

    expected_quality = {
        "assets_with_unknown_license": 0,
        "assets_without_label_provenance": 0,
        "assets_without_positive_duration": 0,
        "assets_without_valid_audio_probe": 0,
        "exact_duplicate_groups": 0,
        "near_duplicate_groups": 0,
    }
    require((coverage.get("asset_quality") or {}) == expected_quality, "coverage asset-quality stop-line drift", failures)

    # Readiness/model-entry remains fail closed.
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-CORPUS-001", "OPEN"), "corpus certificate is not OPEN", failures)
    require(readiness.get("readiness_id") == "EMP-MK1-CORPUS-READINESS-001" and readiness.get("status") == "BLOCKED", "readiness state drift", failures)
    require(readiness.get("eligible_for_certificate_review") is False and readiness.get("modeling_allowed") is False, "model gate opened prematurely", failures)
    require(readiness.get("corpus_certificate", {}).get("status") == "OPEN", "readiness corpus certificate drift", failures)
    require(readiness.get("evidence_identity_sha256") == EXPECTED_EVIDENCE_IDENTITY, "readiness identity drift", failures)
    require(set(readiness.get("gap_codes", [])) == EXPECTED_GAPS, "readiness gap-code set drift; re-audit required", failures)
    ledger_input = readiness.get("inputs", {}).get("canonical_ledger_summary", {})
    require(
        ledger_input.get("baseline_commit") == EXPECTED_LEDGER_BASELINE
        and ledger_input.get("entry_count") == 1141
        and ledger_input.get("ledger_sha256") == EXPECTED_LEDGER_SHA256,
        "readiness ledger input drift",
        failures,
    )
    require((readiness.get("ledger_blocking_reason_counts") or {}) == {}, "readiness reports ledger blockers", failures)
    expected_node_pass = {
        "global_dedup_audit": True,
        "recording_family_audit": True,
        "split_integrity": True,
        "coverage_gate": False,
        "freeze_1_validation": False,
        "freeze_2_validation": False,
        "reproducibility": False,
    }
    nodes = readiness.get("closure_evidence_nodes") or {}
    for name, expected_pass in expected_node_pass.items():
        require(bool((nodes.get(name) or {}).get("pass")) is expected_pass, f"readiness node drift: {name}", failures)

    # Candidate near-duplicate implementation must preserve screen/confirm separation.
    comparison = near_policy.get("comparison") or {}
    require(near_policy.get("policy_id") == "MK1-NEAR-DUP-001", "near-duplicate policy id drift", failures)
    require(comparison.get("candidate_max_distance") == 0.02, "near-duplicate screening threshold drift", failures)
    require(comparison.get("confirmed_group_max_distance") == 0.002, "near-duplicate confirmation threshold drift", failures)
    require(comparison.get("confirmed_group_max_relative_sample_count_delta") == 0.01, "near-duplicate decoded-length confirmation drift", failures)
    require(comparison.get("automatic_merge") is False, "near-duplicate policy must never auto-merge content", failures)
    require(comparison.get("action") == "SCREEN_THEN_CONFIRM_FOR_SPLIT_PROTECTION", "near-duplicate action contract drift", failures)
    require("screening mechanism" in str(near_policy.get("certification_boundary") or ""), "near-duplicate certification boundary lost screening distinction", failures)

    # Release law remains explicit in human-facing authorities.
    require("NO CERT-MK1-DF-CORPUS-001" in docs["state"], "CURRENT-STATE release stop-line missing", failures)
    require("Benchmark A/B/C" in docs["state"] and "modeling_allowed = false" in docs["state"], "model-entry stop-line missing", failures)
    require("PR #37" in docs["doc_audit"] and "no recovered" in docs["doc_audit"].casefold(), "DOC-012 must deny pre-merge recovered credit", failures)

    # Markdown inventory and merge-conflict hygiene.
    md_files = sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)
    require(len(md_files) == EXPECTED_MD_COUNT, f"markdown corpus count drift: {len(md_files)} != {EXPECTED_MD_COUNT}", failures)
    for path in md_files:
        body = path.read_text(encoding="utf-8", errors="replace")
        require("<<<<<<<" not in body and ">>>>>>>" not in body, f"merge-conflict marker in {path.relative_to(ROOT)}", failures)

    if failures:
        print("DOCUMENTATION GOVERNANCE: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    print("DOCUMENTATION GOVERNANCE: PASS")
    print("CERT-DOC-012: CERTIFIED")
    print("audited readiness:", EXPECTED_READINESS_COMMIT)
    print("canonical ledger: 1141 entries / 1141 fingerprints / 0 blockers")
    print("FIRE_ALARM final: 19 assets / 16 groups / 3 sources")
    print("GLASS_SHATTER final: 222 assets / 205 groups / fraction 0.941441")
    print("TIRE_SQUEAL final: 14 assets / 10 groups; HN 25/12/2")
    print("coverage detailed gaps:", len(EXPECTED_COVERAGE_GAPS))
    print("readiness gaps:", len(EXPECTED_GAPS))
    print("near-duplicate contract: screen 0.02 -> confirm 0.002 + <=1% sample delta -> split protection")
    print("corpus certificate: OPEN")
    print("modeling_allowed: false")
    print("markdown corpus files:", len(md_files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
