#!/usr/bin/env python3
"""Fail closed when ECHO documentation/certification truth drifts."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PROMISE = "Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial"
EXPECTED_MD_COUNT = 212
EXPECTED_GAPS = {
    "CORPUS_CERTIFICATE_NOT_CERTIFIED",
    "COVERAGE_GATE_GAP_CODES_NOT_EMPTY",
    "COVERAGE_GATE_NOT_PASS",
    "COVERAGE_GATE_STATUS_NOT_PASS",
    "FIRE_ALARM_ASSETS_10_LT_50",
    "FIRE_ALARM_HARD_NEGATIVE_SOURCES_1_LT_2",
    "FREEZE_1_VALIDATION_NOT_PASS",
    "FREEZE_2_VALIDATION_NOT_PASS",
    "GLASS_SHATTER_HARD_NEGATIVE_SOURCES_1_LT_2",
    "LEDGER_LICENSE_NOT_RELEASE_SAFE_1",
    "LEDGER_SEMANTIC_STATUS_CONFLICT_FIRE_ALARM_1",
    "LEDGER_SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL_1",
    "REPRODUCIBILITY_NOT_PASS",
    "SIREN_HARD_NEGATIVE_SOURCES_1_LT_2",
    "SPLIT_INTEGRITY_NOT_PASS",
    "TIRE_SQUEAL_ASSETS_11_LT_50",
    "TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20",
    "TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2",
    "VEHICLE_HORN_HARD_NEGATIVES_0_LT_20",
    "VEHICLE_HORN_HARD_NEGATIVE_SOURCES_0_LT_2",
}

REQUIRED_FILES = {
    "charter": ROOT / "PROJECT-CHARTER.md",
    "state": ROOT / "CURRENT-STATE.md",
    "doc_standard": ROOT / "governance/DOCUMENTATION-STANDARD.md",
    "doc_coverage": ROOT / "governance/DOCUMENTATION-COVERAGE.md",
    "doc_audit": ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-15-GROUPING-CLOSURE-008.md",
    "cert_ledger": ROOT / "governance/CERTIFICATION-LEDGER.md",
    "free_tier": ROOT / "governance/FREE-TIER-BOUNDARY.md",
    "closure_plan": ROOT / "MK1/build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md",
    "foundry_gates": ROOT / "MK1/build/data-foundry/FOUNDRY-GATES.md",
    "materialization": ROOT / "MK1/build/data-foundry/MATERIALIZATION.md",
    "historical_toolchain_cert": ROOT / "MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-004.md",
    "sonyc_cert": ROOT / "MK1/mining-site/materialization/sonyc-v2.3-materialization-certificate.json",
    "ledger_summary": ROOT / "MK1/mining-site/materialization/canonical-release-safe-asset-ledger-summary.json",
    "dedup": ROOT / "MK1/mining-site/materialization/global-dedup-audit.json",
    "group_audit": ROOT / "MK1/mining-site/materialization/recording-family-audit.json",
    "split": ROOT / "MK1/mining-site/materialization/split-integrity.json",
    "readiness": ROOT / "MK1/mining-site/materialization/corpus-closure-readiness.json",
}


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def ledger_state(body: str, cert_id: str, state: str) -> bool:
    return re.search(rf"\|\s*{re.escape(cert_id)}\s*\|.*\|\s*{re.escape(state)}\s*\|", body) is not None


def load_json(name: str) -> dict:
    return json.loads(REQUIRED_FILES[name].read_text(encoding="utf-8"))


def main() -> int:
    failures: list[str] = []
    for name, path in REQUIRED_FILES.items():
        require(path.is_file(), f"missing required authority: {name} -> {path.relative_to(ROOT)}", failures)
    if failures:
        print("DOCUMENTATION GOVERNANCE: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    json_names = {"readiness", "sonyc_cert", "ledger_summary", "dedup", "group_audit", "split"}
    docs = {name: text(path) for name, path in REQUIRED_FILES.items() if name not in json_names}
    readiness = load_json("readiness")
    sonyc = load_json("sonyc_cert")
    ledger = load_json("ledger_summary")
    dedup = load_json("dedup")
    group_audit = load_json("group_audit")
    split = load_json("split")

    # Immutable ancestors.
    require(PROMISE in docs["charter"], "immutable promise missing from charter", failures)
    require(PROMISE in docs["state"], "immutable promise missing from current state", failures)
    require("FROZEN_DOCUMENTATION_GOVERNANCE" in docs["doc_standard"], "documentation governance not frozen", failures)
    require("documentation-first" in docs["doc_standard"].casefold(), "documentation-first rule missing", failures)
    require("ECHO-FREE-TIER-001" in docs["doc_standard"], "documentation standard lacks free-tier ancestor", failures)
    require("FROZEN_GLOBAL_POLICY" in docs["free_tier"], "free-tier policy not frozen", failures)
    require("0 USD" in docs["free_tier"], "zero-cost invariant missing", failures)

    # Documentation lineage.
    require("CERT-DOC-008" in docs["doc_coverage"] and "Current certificate" in docs["doc_coverage"], "DOCUMENTATION-COVERAGE does not name DOC-008 current", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-008", "CERTIFIED"), "CERT-DOC-008 not certified in ledger", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-007", "INVALIDATED"), "CERT-DOC-007 must be invalidated", failures)
    require("CERT-DOC-008                = CERTIFIED / current" in docs["state"], "CURRENT-STATE does not show DOC-008 current", failures)
    require("**Certificate:** `CERT-DOC-008`" in docs["doc_audit"], "current audit does not bind DOC-008", failures)
    require("**Status:** `CERTIFIED`" in docs["doc_audit"], "DOC-008 audit not certified", failures)
    require("8e7702a2bf629642f78859763dabbe09df03df02" in docs["doc_audit"], "DOC-008 missing audited readiness commit", failures)

    # Toolchain lineage remains fail-closed while active semantics change.
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-TOOLCHAIN-004", "INVALIDATED"), "toolchain-004 must be invalidated", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-TOOLCHAIN-005", "CANDIDATE"), "toolchain-005 must remain candidate", failures)
    require("CERT-MK1-DF-TOOLCHAIN-005 = CANDIDATE" in docs["foundry_gates"], "FOUNDRY-GATES missing toolchain-005 candidate", failures)

    # SONYC scoped certificate remains exact.
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-SONYC-001", "CERTIFIED"), "SONYC certificate missing/not certified", failures)
    require(sonyc.get("schema_version") == "echo.cert.v1", "unexpected SONYC certificate schema", failures)
    require(sonyc.get("artifact_id") == "CERT-MK1-DF-SONYC-001", "unexpected SONYC certificate id", failures)
    require(sonyc.get("status") == "CERTIFIED", "SONYC certificate must be CERTIFIED", failures)
    require(sonyc.get("implementation_baseline") == "ab8c47ba6aabb25390644954a2a06945ca7a81bb", "SONYC implementation baseline drift", failures)
    require(sonyc.get("materialization_run_id") == 34922010537, "SONYC materialization run drift", failures)
    require(sonyc.get("durable_evidence_commit") == "78fc019839f1c9dad1a58a70d439605d887361d7", "SONYC evidence commit drift", failures)
    sonyc_summary = sonyc.get("materialization_summary", {})
    require(sonyc_summary.get("shards_expected") == 19 and sonyc_summary.get("shards_materialized") == 19, "SONYC shard closure drift", failures)
    require(sonyc_summary.get("asset_count") == 18510, "SONYC release asset count drift", failures)
    require(sonyc_summary.get("fingerprinted_ledger_relevant_assets") == 599, "SONYC fingerprint count drift", failures)
    require(sonyc_summary.get("probe_failures") == 0 and sonyc_summary.get("fingerprint_failures") == 0, "SONYC technical failures must stay zero", failures)
    require(sonyc.get("free_tier_boundary", {}).get("result") == "PASS", "SONYC free-tier result drift", failures)

    # Canonical ledger after global grouping.
    require(ledger.get("baseline_commit") == "8c547b70d23ce6c592ddd20d55ff37df9fa7fa03", "canonical ledger baseline drift", failures)
    require(ledger.get("entry_count") == 1081, "canonical ledger entry count drift", failures)
    require(ledger.get("canonical_fingerprint_count") == 1081 and ledger.get("canonical_fingerprint_missing_count") == 0, "canonical fingerprint closure drift", failures)
    grouping = ledger.get("global_recording_group_resolution") or {}
    require(grouping.get("status") == "PASS", "global recording-group resolution not PASS", failures)
    require(grouping.get("fallback_asset_count_before") == 448 and grouping.get("fallback_asset_count_after") == 0, "fallback grouping closure drift", failures)
    require(grouping.get("global_acoustic_component_count") == 17, "global acoustic component count drift", failures)
    require(grouping.get("members_reassigned_to_global_acoustic_component") == 97, "global component membership drift", failures)
    require(grouping.get("content_deleted") is False and grouping.get("content_merge_performed") is False, "grouping must not merge/delete content", failures)
    blockers = ledger.get("blocking_reason_counts") or {}
    require(blockers == {"LICENSE_NOT_RELEASE_SAFE": 1, "SEMANTIC_STATUS_CONFLICT_FIRE_ALARM": 1, "SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL": 1}, "ledger blocker set drift", failures)

    # Global duplicate/family nodes are now empirically closed.
    require(dedup.get("status") == "PASS" and dedup.get("gap_codes") == [], "global dedup must remain PASS", failures)
    require(dedup.get("missing_fingerprint_count") == 0, "dedup fingerprint coverage regressed", failures)
    require(dedup.get("exact_cross_recording_group_conflict_count") == 0, "exact identity crosses recording groups", failures)
    require(dedup.get("near_duplicate_unresolved_cross_group_count") == 0, "near-duplicate relation crosses recording groups", failures)
    require(group_audit.get("status") == "PASS" and group_audit.get("gap_codes") == [], "recording-family audit must remain PASS", failures)
    require(group_audit.get("missing_recording_group_count") == 0 and group_audit.get("pending_global_group_audit_count") == 0, "recording-family closure regressed", failures)

    # Split remains a genuine fail-closed blocker with an exact audited shape.
    require(split.get("status") == "FAIL", "split integrity unexpectedly changed without audit", failures)
    require(split.get("original_split_conflict_count") == 3, "split conflict count drift", failures)
    require(split.get("split_asset_counts", {}).get("UNASSIGNED") == 62, "unassigned split asset count drift", failures)
    require(set(split.get("gap_codes") or []) == {"ELIGIBLE_ASSET_WITHOUT_SPLIT", "ORIGINAL_SPLIT_CONFLICT_WITHIN_RECORDING_FAMILY"}, "split gap set drift", failures)

    # Final corpus/model gate remains fail-closed.
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-CORPUS-001", "OPEN"), "corpus certificate is not OPEN", failures)
    require(readiness.get("readiness_id") == "EMP-MK1-CORPUS-READINESS-001", "unexpected readiness id", failures)
    require(readiness.get("status") == "BLOCKED", "readiness must remain BLOCKED", failures)
    require(readiness.get("eligible_for_certificate_review") is False, "certificate review must remain ineligible", failures)
    require(readiness.get("modeling_allowed") is False, "modeling_allowed must remain false", failures)
    require(readiness.get("corpus_certificate", {}).get("status") == "OPEN", "readiness corpus certificate state drift", failures)
    require(readiness.get("evidence_identity_sha256") == "fcd07c11d3291d5a78ee28cae93e42de0f16e78522720e78fffb5e71b4bcf129", "readiness identity drift", failures)
    require(set(readiness.get("gap_codes", [])) == EXPECTED_GAPS, "readiness gap-code set drift; re-audit required", failures)
    require(readiness.get("inputs", {}).get("canonical_ledger_summary", {}).get("entry_count") == 1081, "readiness ledger count drift", failures)

    expected_node_pass = {
        "global_dedup_audit": True,
        "recording_family_audit": True,
        "coverage_gate": False,
        "freeze_1_validation": False,
        "freeze_2_validation": False,
        "reproducibility": False,
        "split_integrity": False,
    }
    for key, expected_pass in expected_node_pass.items():
        node = readiness.get("closure_evidence_nodes", {}).get(key, {})
        require(node.get("present") is True, f"closure node missing: {key}", failures)
        require(node.get("pass") is expected_pass, f"closure node pass-state drift: {key}", failures)

    closure_joined = docs["closure_plan"] + "\n" + docs["foundry_gates"] + "\n" + docs["state"]
    for marker in ("near-duplicate", "hard-negative", "recording-family", "freeze #2", "gap_codes", "model-entry"):
        require(marker.casefold() in closure_joined.casefold(), f"closure marker missing: {marker}", failures)

    materialization_cf = docs["materialization"].casefold()
    require("requires a persistent self-hosted" not in materialization_cf, "stale self-hosted requirement reintroduced", failures)
    require("120 gib" not in materialization_cf, "stale 120 GiB requirement reintroduced", failures)
    require("echo-free-tier-001" in materialization_cf and "bounded" in materialization_cf, "materialization guide lacks bounded free-tier execution", failures)

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
    print("documentation certificate: CERT-DOC-008")
    print("toolchain: CERT-MK1-DF-TOOLCHAIN-005 CANDIDATE")
    print("SONYC: CERT-MK1-DF-SONYC-001 CERTIFIED")
    print("canonical fingerprints: 1081/1081")
    print("global dedup: PASS")
    print("recording-family audit: PASS")
    print("split integrity: FAIL / 3 conflicts / 62 unassigned")
    print("corpus certificate: OPEN")
    print("modeling_allowed: false")
    print("markdown corpus files:", len(md_files))
    print("global boundary: ECHO-FREE-TIER-001")
    return 0


if __name__ == "__main__":
    sys.exit(main())
