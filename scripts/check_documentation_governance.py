#!/usr/bin/env python3
"""Fail closed when ECHO documentation/certification truth drifts."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PROMISE = "Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial"
EXPECTED_MD_COUNT = 210
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
    "GLOBAL_DEDUP_AUDIT_NOT_PASS",
    "LEDGER_AUGMENTATION_ONLY_NO_REAL_SOURCE_CREDIT_4",
    "LEDGER_GROUPING_GLOBAL_AUDIT_REQUIRED_503",
    "LEDGER_LICENSE_NOT_RELEASE_SAFE_1",
    "LEDGER_NO_EXACT_SEMANTIC_ROLE_83",
    "LEDGER_RIGHTS_TEXT_CONFLICT_REVIEW_REQUIRED_1",
    "LEDGER_SEMANTIC_STATUS_CONFLICT_FIRE_ALARM_1",
    "LEDGER_SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL_1",
    "RECORDING_FAMILY_AUDIT_NOT_PASS",
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
    "doc_audit": ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-14-SONYC-RECERTIFICATION.md",
    "cert_ledger": ROOT / "governance/CERTIFICATION-LEDGER.md",
    "free_tier": ROOT / "governance/FREE-TIER-BOUNDARY.md",
    "closure_plan": ROOT / "MK1/build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md",
    "foundry_gates": ROOT / "MK1/build/data-foundry/FOUNDRY-GATES.md",
    "materialization": ROOT / "MK1/build/data-foundry/MATERIALIZATION.md",
    "toolchain_cert": ROOT / "MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-004.md",
    "sonyc_cert": ROOT / "MK1/mining-site/materialization/sonyc-v2.3-materialization-certificate.json",
    "ledger_summary": ROOT / "MK1/mining-site/materialization/canonical-release-safe-asset-ledger-summary.json",
    "readiness": ROOT / "MK1/mining-site/materialization/corpus-closure-readiness.json",
}


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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

    json_names = {"readiness", "sonyc_cert", "ledger_summary"}
    docs = {name: text(path) for name, path in REQUIRED_FILES.items() if name not in json_names}
    readiness = json.loads(REQUIRED_FILES["readiness"].read_text(encoding="utf-8"))
    sonyc = json.loads(REQUIRED_FILES["sonyc_cert"].read_text(encoding="utf-8"))
    ledger_summary = json.loads(REQUIRED_FILES["ledger_summary"].read_text(encoding="utf-8"))

    require(PROMISE in docs["charter"], "immutable promise missing from charter", failures)
    require(PROMISE in docs["state"], "immutable promise missing from current state", failures)
    require("FROZEN_DOCUMENTATION_GOVERNANCE" in docs["doc_standard"], "documentation governance not frozen", failures)
    require("documentation-first" in docs["doc_standard"].casefold(), "documentation-first rule missing", failures)
    require("ECHO-FREE-TIER-001" in docs["doc_standard"], "documentation standard does not inherit free-tier boundary", failures)
    require("FROZEN_GLOBAL_POLICY" in docs["free_tier"], "free-tier policy not frozen", failures)
    require("0 USD" in docs["free_tier"], "zero-cost invariant missing", failures)

    # Documentation lineage.
    require("CERT-DOC-006" in docs["doc_coverage"] and "Current certificate" in docs["doc_coverage"], "DOCUMENTATION-COVERAGE does not name CERT-DOC-006 as current", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-006", "CERTIFIED"), "CERT-DOC-006 not certified in ledger", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-005", "INVALIDATED"), "CERT-DOC-005 must be invalidated", failures)
    require("CERT-DOC-006                = CERTIFIED / current" in docs["state"], "CURRENT-STATE does not show CERT-DOC-006 current", failures)
    require("**Certificate:** `CERT-DOC-006`" in docs["doc_audit"], "current audit does not bind CERT-DOC-006", failures)
    require("**Status:** `CERTIFIED`" in docs["doc_audit"], "current documentation audit not certified", failures)

    # Toolchain lineage.
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-TOOLCHAIN-004", "CERTIFIED"), "toolchain-004 missing/not certified", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-TOOLCHAIN-003", "INVALIDATED"), "toolchain-003 must be invalidated", failures)
    require("CERT-MK1-DF-TOOLCHAIN-004  = CERTIFIED / current" in docs["state"], "CURRENT-STATE does not show toolchain-004 current", failures)
    require("CERT-MK1-DF-TOOLCHAIN-004" in docs["foundry_gates"], "FOUNDRY-GATES does not point to toolchain-004", failures)
    require("34922010529" in docs["toolchain_cert"], "toolchain-004 record missing Data Foundry CI run", failures)
    require("34922010537" in docs["toolchain_cert"], "toolchain-004 record missing real SONYC run", failures)
    require("ab8c47ba6aabb25390644954a2a06945ca7a81bb" in docs["toolchain_cert"], "toolchain-004 record missing certified implementation baseline", failures)

    # SONYC scoped empirical certificate.
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-SONYC-001", "CERTIFIED"), "SONYC certificate missing/not certified in ledger", failures)
    require(sonyc.get("schema_version") == "echo.cert.v1", "unexpected SONYC certificate schema", failures)
    require(sonyc.get("artifact_id") == "CERT-MK1-DF-SONYC-001", "unexpected SONYC certificate id", failures)
    require(sonyc.get("status") == "CERTIFIED", "SONYC certificate must be CERTIFIED", failures)
    require(sonyc.get("implementation_baseline") == "ab8c47ba6aabb25390644954a2a06945ca7a81bb", "SONYC implementation baseline drift", failures)
    require(sonyc.get("materialization_run_id") == 34922010537, "SONYC materialization run drift", failures)
    require(sonyc.get("durable_evidence_commit") == "78fc019839f1c9dad1a58a70d439605d887361d7", "SONYC durable evidence commit drift", failures)
    summary = sonyc.get("materialization_summary", {})
    require(summary.get("shards_expected") == 19 and summary.get("shards_materialized") == 19, "SONYC shard closure must remain 19/19", failures)
    require(summary.get("asset_count") == 18510, "SONYC release asset count drift", failures)
    require(summary.get("target_candidate_count") == 236, "SONYC target candidate count drift", failures)
    require(summary.get("confuser_candidate_count") == 428, "SONYC confuser candidate count drift", failures)
    require(summary.get("fingerprinted_ledger_relevant_assets") == 599, "SONYC fingerprinted asset count drift", failures)
    require(summary.get("probe_failures") == 0, "SONYC probe failures must be zero", failures)
    require(summary.get("fingerprint_failures") == 0, "SONYC fingerprint failures must be zero", failures)
    require(sonyc.get("free_tier_boundary", {}).get("policy_id") == "ECHO-FREE-TIER-001", "SONYC certificate missing free-tier ancestor", failures)
    require(sonyc.get("free_tier_boundary", {}).get("result") == "PASS", "SONYC free-tier result must be PASS", failures)

    # Canonical ledger exact truth.
    require(ledger_summary.get("baseline_commit") == "78fc019839f1c9dad1a58a70d439605d887361d7", "canonical ledger baseline drift", failures)
    require(ledger_summary.get("entry_count") == 1164, "canonical ledger entry count drift", failures)
    require(ledger_summary.get("canonical_fingerprint_count") == 1164, "canonical fingerprint count drift", failures)
    require(ledger_summary.get("canonical_fingerprint_missing_count") == 0, "canonical fingerprint closure regressed", failures)
    require(ledger_summary.get("status") == "PASS_CONSOLIDATED_WITH_OPEN_GATES", "unexpected canonical ledger status", failures)
    require(ledger_summary.get("positive_counts") == {"FIRE_ALARM": 10, "GLASS_SHATTER": 304, "SIREN": 175, "TIRE_SQUEAL": 11, "VEHICLE_HORN": 245}, "canonical positive counts drift", failures)
    require(ledger_summary.get("hard_negative_counts") == {"FIRE_ALARM": 34, "GLASS_SHATTER": 401, "SIREN": 32, "TIRE_SQUEAL": 0, "VEHICLE_HORN": 0}, "canonical hard-negative counts drift", failures)

    # Final corpus/model gate remains fail-closed.
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-CORPUS-001", "OPEN"), "corpus certificate is not explicitly OPEN", failures)
    require("CERT-MK1-DF-CORPUS-001     = OPEN" in docs["state"], "CURRENT-STATE does not keep corpus certificate OPEN", failures)
    require(readiness.get("readiness_id") == "EMP-MK1-CORPUS-READINESS-001", "unexpected readiness id", failures)
    require(readiness.get("status") == "BLOCKED", "readiness must remain BLOCKED for current empirical baseline", failures)
    require(readiness.get("eligible_for_certificate_review") is False, "certificate review must remain ineligible", failures)
    require(readiness.get("modeling_allowed") is False, "modeling_allowed must remain false while corpus OPEN", failures)
    require(readiness.get("corpus_certificate", {}).get("status") == "OPEN", "readiness corpus certificate status drift", failures)
    require(set(readiness.get("gap_codes", [])) == EXPECTED_GAPS, "readiness gap-code set drift; re-audit required", failures)
    require(readiness.get("inputs", {}).get("canonical_ledger_summary", {}).get("entry_count") == 1164, "readiness ledger input count drift", failures)

    for key in ("coverage_gate", "freeze_1_validation", "freeze_2_validation", "global_dedup_audit", "recording_family_audit", "reproducibility", "split_integrity"):
        node = readiness.get("closure_evidence_nodes", {}).get(key, {})
        require(node.get("present") is True, f"closure node missing: {key}", failures)
        require(node.get("pass") is False, f"closure node unexpectedly PASS without corpus re-audit: {key}", failures)

    closure_joined = docs["closure_plan"] + "\n" + docs["foundry_gates"] + "\n" + docs["state"]
    for marker in ("near-duplicate", "hard-negative", "recording-family", "second clean freeze", "gap_codes", "model-entry"):
        require(marker.casefold() in closure_joined.casefold(), f"closure marker missing: {marker}", failures)

    materialization_cf = docs["materialization"].casefold()
    require("requires a persistent self-hosted" not in materialization_cf, "stale self-hosted requirement reintroduced", failures)
    require("120 gib" not in materialization_cf, "stale 120 GiB requirement reintroduced", failures)
    require("echo-free-tier-001" in materialization_cf, "materialization guide lacks free-tier boundary", failures)
    require("bounded" in materialization_cf, "materialization guide lacks bounded execution model", failures)

    md_files = sorted(ROOT.rglob("*.md"))
    require(len(md_files) == EXPECTED_MD_COUNT, f"Markdown corpus drift: expected {EXPECTED_MD_COUNT}, found {len(md_files)}; documentation re-audit required", failures)
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
    print("immutable promise: PASS")
    print("documentation certificate: CERT-DOC-006")
    print("foundry toolchain certificate: CERT-MK1-DF-TOOLCHAIN-004")
    print("SONYC materialization certificate: CERT-MK1-DF-SONYC-001")
    print("canonical fingerprints: 1164/1164")
    print("corpus readiness: BLOCKED with exact audited gaps")
    print("corpus certificate: OPEN")
    print("modeling_allowed: false")
    print("markdown corpus files:", len(md_files))
    print("global boundary: ECHO-FREE-TIER-001")
    return 0


if __name__ == "__main__":
    sys.exit(main())
