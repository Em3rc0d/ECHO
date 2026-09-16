#!/usr/bin/env python3
"""Fail closed when ECHO documentation/certification truth drifts."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PROMISE = "Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial"
EXPECTED_MD_COUNT = 215
EXPECTED_READINESS_COMMIT = "2088c93d65b5d4dff58bb5cdb91b0e76e6288afb"
EXPECTED_EVIDENCE_IDENTITY = "9b6da43da378dbf546a3961c6ed47b8e7218b5135bbe84680f58eecf86030559"
EXPECTED_LEDGER_BASELINE = "0e05b9ce7ef9afdbd6d0d327922f9811fa0a50d7"
EXPECTED_LEDGER_SHA256 = "b250b18e8ccef3776cdc38d42f240a057bcf99b260cc6cb58a77aad93e9d0cab"
EXPECTED_COVERAGE_LEDGER_SHA256 = "9ca05a6c2a405f5e2003a06349f048fe0c6cb65454e64f42cd2c34c0556a3dc5"
EXPECTED_GAPS = {
    "CORPUS_CERTIFICATE_NOT_CERTIFIED",
    "COVERAGE_GATE_GAP_CODES_NOT_EMPTY",
    "COVERAGE_GATE_NOT_PASS",
    "COVERAGE_GATE_STATUS_NOT_PASS",
    "FIRE_ALARM_ASSETS_12_LT_50",
    "FREEZE_1_VALIDATION_NOT_PASS",
    "FREEZE_2_VALIDATION_NOT_PASS",
    "REPRODUCIBILITY_NOT_PASS",
    "TIRE_SQUEAL_ASSETS_11_LT_50",
}
EXPECTED_COVERAGE_GAPS = {
    "FIRE_ALARM_ASSETS_BELOW_MIN",
    "FIRE_ALARM_GROUPS_BELOW_MIN",
    "FIRE_ALARM_TEST_ASSETS_BELOW_MIN",
    "FIRE_ALARM_TEST_GROUPS_BELOW_MIN",
    "FIRE_ALARM_TRAIN_ASSETS_BELOW_MIN",
    "FIRE_ALARM_TRAIN_GROUPS_BELOW_MIN",
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
    "doc_audit": ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-15-CORPUS-CLOSURE-011.md",
    "cert_ledger": ROOT / "governance/CERTIFICATION-LEDGER.md",
    "free_tier": ROOT / "governance/FREE-TIER-BOUNDARY.md",
    "foundry_gates": ROOT / "MK1/build/data-foundry/FOUNDRY-GATES.md",
    "materialization": ROOT / "MK1/build/data-foundry/MATERIALIZATION.md",
    "sonyc_cert": ROOT / "MK1/mining-site/materialization/sonyc-v2.3-materialization-certificate.json",
    "ledger_summary": ROOT / "MK1/mining-site/materialization/canonical-release-safe-asset-ledger-summary.json",
    "dedup": ROOT / "MK1/mining-site/materialization/global-dedup-audit.json",
    "group_audit": ROOT / "MK1/mining-site/materialization/recording-family-audit.json",
    "split": ROOT / "MK1/mining-site/materialization/split-integrity.json",
    "coverage": ROOT / "MK1/mining-site/materialization/coverage-gate.json",
    "readiness": ROOT / "MK1/mining-site/materialization/corpus-closure-readiness.json",
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

    json_names = {"readiness", "sonyc_cert", "ledger_summary", "dedup", "group_audit", "split", "coverage"}
    docs = {name: text(path) for name, path in REQUIRED_FILES.items() if name not in json_names}
    readiness = load_json("readiness")
    sonyc = load_json("sonyc_cert")
    ledger = load_json("ledger_summary")
    dedup = load_json("dedup")
    group_audit = load_json("group_audit")
    split = load_json("split")
    coverage = load_json("coverage")

    # Immutable product and zero-cost ancestors.
    require(PROMISE in docs["charter"], "immutable promise missing from charter", failures)
    require(PROMISE in docs["state"], "immutable promise missing from current state", failures)
    require("FROZEN_DOCUMENTATION_GOVERNANCE" in docs["doc_standard"], "documentation governance not frozen", failures)
    require("ECHO-FREE-TIER-001" in docs["doc_standard"] and "FROZEN_GLOBAL_POLICY" in docs["free_tier"], "free-tier ancestor drift", failures)
    require("0 USD" in docs["free_tier"], "zero-cost invariant missing", failures)

    # Documentation and certification lineage.
    require("CERT-DOC-011" in docs["doc_coverage"] and "Current certificate" in docs["doc_coverage"], "DOCUMENTATION-COVERAGE does not name DOC-011 current", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-011", "CERTIFIED"), "CERT-DOC-011 not certified in ledger", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-001..010", "INVALIDATED"), "historical DOC certificates not invalidated", failures)
    require("CERT-DOC-011" in docs["state"] and "CERTIFIED / current" in docs["state"], "CURRENT-STATE does not show DOC-011 current", failures)
    require("**Certificate:** `CERT-DOC-011`" in docs["doc_audit"] and "**Status:** `CERTIFIED`" in docs["doc_audit"], "DOC-011 audit not certified", failures)
    require(EXPECTED_READINESS_COMMIT in docs["doc_audit"], "DOC-011 missing audited readiness commit", failures)
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

    # Canonical ledger after durable Wikimedia FIRE expansion.
    require(ledger.get("baseline_commit") == EXPECTED_LEDGER_BASELINE, "canonical ledger baseline drift", failures)
    require(ledger.get("entry_count") == 1162, "canonical ledger entry count drift", failures)
    require(ledger.get("ledger_sha256") == EXPECTED_LEDGER_SHA256, "canonical ledger identity drift", failures)
    require(ledger.get("canonical_fingerprint_count") == 1162 and ledger.get("canonical_fingerprint_missing_count") == 0, "canonical fingerprint closure drift", failures)
    require((ledger.get("blocking_reason_counts") or {}) == {}, "corpus-facing ledger blockers reappeared", failures)
    source_counts = ledger.get("source_asset_counts") or {}
    require(source_counts.get("echo-wikimedia-fire-alarm-v1") == 7, "Wikimedia source count drift", failures)
    require(source_counts.get("echo-bigsoundbank-cc0-gap-v1") == 53, "BigSoundBank source count drift", failures)
    grouping = ledger.get("global_recording_group_resolution") or {}
    require(grouping.get("status") == "PASS", "global grouping not PASS", failures)
    require(grouping.get("fallback_asset_count_after") == 0, "fallback grouping closure regressed", failures)
    require(grouping.get("global_acoustic_component_count") == 14, "global acoustic component count drift", failures)
    require(grouping.get("members_reassigned_to_global_acoustic_component") == 125, "global component membership drift", failures)
    require(grouping.get("content_deleted") is False and grouping.get("content_merge_performed") is False, "grouping must not merge/delete content", failures)
    expected_positive = {"FIRE_ALARM": 12, "GLASS_SHATTER": 320, "SIREN": 173, "TIRE_SQUEAL": 11, "VEHICLE_HORN": 245}
    expected_hn = {"FIRE_ALARM": 206, "GLASS_SHATTER": 440, "SIREN": 245, "TIRE_SQUEAL": 25, "VEHICLE_HORN": 146}
    expected_hn_sources = {"FIRE_ALARM": 4, "GLASS_SHATTER": 2, "SIREN": 4, "TIRE_SQUEAL": 2, "VEHICLE_HORN": 3}
    require(ledger.get("positive_counts") == expected_positive, "positive corpus counts drift", failures)
    require(ledger.get("hard_negative_counts") == expected_hn, "hard-negative counts drift", failures)
    require(ledger.get("hard_negative_underlying_source_family_counts") == expected_hn_sources, "hard-negative source-family counts drift", failures)

    # Structural nodes remain closed without hiding protected conflicts.
    require(dedup.get("status") == "PASS" and dedup.get("gap_codes") == [], "global dedup must remain PASS", failures)
    require(group_audit.get("status") == "PASS" and group_audit.get("gap_codes") == [], "recording-family audit must remain PASS", failures)
    require(split.get("status") == "PASS" and split.get("gap_codes") == [], "split integrity must remain PASS", failures)
    require(split.get("original_split_conflict_count") == 2, "split conflict count drift", failures)
    require(split.get("original_split_conflicts_quarantined") == 2, "all protected split conflicts must stay quarantined", failures)
    require(split.get("quarantined_asset_count") == 93, "quarantined asset count drift", failures)

    # Final coverage truth.
    require(coverage.get("status") == "FAIL", "coverage unexpectedly not FAIL; re-audit required", failures)
    require(coverage.get("ledger_sha256") == EXPECTED_COVERAGE_LEDGER_SHA256, "coverage ledger identity drift", failures)
    coverage_gaps = set(coverage.get("gap_codes", []))
    require(coverage_gaps == EXPECTED_COVERAGE_GAPS, "coverage gap-code set drift; re-audit required", failures)
    require(coverage.get("quarantined_split_conflict_asset_count") == 93, "coverage quarantine count drift", failures)
    background = coverage.get("background") or {}
    require((background.get("asset_count"), background.get("independent_group_count"), background.get("source_count")) == (416, 383, 4), "background closure drift", failures)
    classes = coverage.get("classes") or {}
    fire = classes.get("FIRE_ALARM") or {}
    require((fire.get("asset_count"), fire.get("independent_group_count"), fire.get("source_count")) == (12, 9, 3), "FIRE final coverage drift", failures)
    require(fire.get("split_assets") == {"test": 0, "train": 10, "validation": 2}, "FIRE split asset drift", failures)
    require(fire.get("split_groups") == {"test": 0, "train": 7, "validation": 2}, "FIRE split group drift", failures)
    require(fire.get("source_asset_counts") == {"BIGSOUNDBANK": 4, "FREESOUND": 5, "WIKIMEDIA_COMMONS": 3}, "FIRE source counts drift", failures)
    require(abs(float(fire.get("clip_duration_seconds") or 0.0) - 311.05767) < 1e-6, "FIRE duration drift", failures)
    glass = classes.get("GLASS_SHATTER") or {}
    require((glass.get("asset_count"), glass.get("independent_group_count"), glass.get("source_count")) == (239, 222, 4), "GLASS final coverage drift", failures)
    require(glass.get("max_single_source_fraction") == 0.945607, "GLASS concentration drift", failures)
    require(glass.get("source_asset_counts") == {"BIGSOUNDBANK": 6, "FREESOUND": 226, "OPENGAMEART_RUBBERDUCK": 6, "OPENGAMEART_TILL_BEHREND": 1}, "GLASS source counts drift", failures)
    tire = classes.get("TIRE_SQUEAL") or {}
    require((tire.get("asset_count"), tire.get("independent_group_count")) == (11, 11), "TIRE positive closure drift", failures)
    tire_hn = tire.get("hard_negatives") or {}
    require((tire_hn.get("asset_count"), tire_hn.get("independent_group_count"), tire_hn.get("source_count")) == (25, 12, 2), "TIRE hard-negative closure drift", failures)
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
    require(ledger_input.get("baseline_commit") == EXPECTED_LEDGER_BASELINE and ledger_input.get("entry_count") == 1162 and ledger_input.get("ledger_sha256") == EXPECTED_LEDGER_SHA256, "readiness ledger input drift", failures)
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
    for key, expected_pass in expected_node_pass.items():
        node = readiness.get("closure_evidence_nodes", {}).get(key, {})
        require(node.get("present") is True and node.get("pass") is expected_pass, f"closure node drift: {key}", failures)

    # Product-direction and materialization guardrails.
    joined = "\n".join(docs.values())
    for marker in ("Benchmark A/B/C", "Event Engine", "Edge Agent", "MQTT", "real camera", "modeling_allowed", "hard-negative", "freeze #2"):
        require(marker.casefold() in joined.casefold(), f"product/closure marker missing: {marker}", failures)
    require("CORPUS-001" in joined, "corpus-to-model dependency missing", failures)
    materialization_cf = docs["materialization"].casefold()
    require("requires a persistent self-hosted" not in materialization_cf and "120 gib" not in materialization_cf, "stale materialization requirement reintroduced", failures)
    require("echo-free-tier-001" in materialization_cf and "bounded" in materialization_cf, "materialization guide lacks bounded free-tier execution", failures)

    # Documentation inventory and merge integrity.
    md_files = sorted(ROOT.rglob("*.md"))
    require(len(md_files) == EXPECTED_MD_COUNT, f"Markdown corpus drift: expected {EXPECTED_MD_COUNT}, found {len(md_files)}; re-audit required", failures)
    for path in md_files:
        body = text(path)
        if "<<<<<<< " in body or ("=======\n" in body and ">>>>>>> " in body):
            failures.append(f"merge conflict marker found in {path.relative_to(ROOT)}")

    if failures:
        print("DOCUMENTATION GOVERNANCE: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    print("DOCUMENTATION GOVERNANCE: PASS")
    print("documentation certificate: CERT-DOC-011")
    print("canonical fingerprints: 1162/1162")
    print("FIRE_ALARM final: 12 assets / 9 groups / 3 sources")
    print("GLASS_SHATTER final: 239 assets / 222 groups / fraction 0.945607")
    print("TIRE_SQUEAL final: 11 assets / 11 groups; HN 25/12/2")
    print("coverage detailed gaps:", len(EXPECTED_COVERAGE_GAPS))
    print("readiness gaps:", len(EXPECTED_GAPS))
    print("corpus certificate: OPEN")
    print("modeling_allowed: false")
    print("markdown corpus files:", len(md_files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
