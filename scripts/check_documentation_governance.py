#!/usr/bin/env python3
"""Fail closed when ECHO documentation/certification truth drifts."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PROMISE = "Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial"
EXPECTED_MD_COUNT = 213
EXPECTED_READINESS_COMMIT = "d94eff2958bbe57076610524cbb192d14ec95739"
EXPECTED_EVIDENCE_IDENTITY = "90f2dd006cfbacfe9dc1bdc5cb81c7d9411ccf5322d6ca2dd53f334e76c209e8"
EXPECTED_LEDGER_BASELINE = "4b261bd10d6578a6256fca8ec848ea1055c24b32"
EXPECTED_LEDGER_SHA256 = "36ef8e19198a296d7806106adc2c4ee43b7827d893e78b6bbd2d1ffd83b3743a"
EXPECTED_GAPS = {
    "CORPUS_CERTIFICATE_NOT_CERTIFIED",
    "COVERAGE_GATE_GAP_CODES_NOT_EMPTY",
    "COVERAGE_GATE_NOT_PASS",
    "COVERAGE_GATE_STATUS_NOT_PASS",
    "FIRE_ALARM_ASSETS_9_LT_50",
    "FIRE_ALARM_HARD_NEGATIVE_SOURCES_1_LT_2",
    "FREEZE_1_VALIDATION_NOT_PASS",
    "FREEZE_2_VALIDATION_NOT_PASS",
    "GLASS_SHATTER_HARD_NEGATIVE_SOURCES_1_LT_2",
    "REPRODUCIBILITY_NOT_PASS",
    "SIREN_HARD_NEGATIVE_SOURCES_1_LT_2",
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
    "doc_audit": ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-15-CORPUS-CLOSURE-009.md",
    "cert_ledger": ROOT / "governance/CERTIFICATION-LEDGER.md",
    "free_tier": ROOT / "governance/FREE-TIER-BOUNDARY.md",
    "foundry_gates": ROOT / "MK1/build/data-foundry/FOUNDRY-GATES.md",
    "materialization": ROOT / "MK1/build/data-foundry/MATERIALIZATION.md",
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

    # Immutable product and execution ancestors.
    require(PROMISE in docs["charter"], "immutable promise missing from charter", failures)
    require(PROMISE in docs["state"], "immutable promise missing from current state", failures)
    require("FROZEN_DOCUMENTATION_GOVERNANCE" in docs["doc_standard"], "documentation governance not frozen", failures)
    require("documentation-first" in docs["doc_standard"].casefold(), "documentation-first rule missing", failures)
    require("ECHO-FREE-TIER-001" in docs["doc_standard"], "documentation standard lacks free-tier ancestor", failures)
    require("FROZEN_GLOBAL_POLICY" in docs["free_tier"], "free-tier policy not frozen", failures)
    require("0 USD" in docs["free_tier"], "zero-cost invariant missing", failures)

    # Documentation lineage.
    require("CERT-DOC-009" in docs["doc_coverage"] and "Current certificate" in docs["doc_coverage"], "DOCUMENTATION-COVERAGE does not name DOC-009 current", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-009", "CERTIFIED"), "CERT-DOC-009 not certified in ledger", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-001..008", "INVALIDATED"), "historical DOC certificates must be invalidated", failures)
    require("CERT-DOC-009                   = CERTIFIED / current" in docs["state"], "CURRENT-STATE does not show DOC-009 current", failures)
    require("**Certificate:** `CERT-DOC-009`" in docs["doc_audit"], "current audit does not bind DOC-009", failures)
    require("**Status:** `CERTIFIED`" in docs["doc_audit"], "DOC-009 audit not certified", failures)
    require(EXPECTED_READINESS_COMMIT in docs["doc_audit"], "DOC-009 missing audited readiness commit", failures)

    # Toolchain lineage remains fail-closed while closure is active.
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

    # Current canonical corpus-facing ledger.
    require(ledger.get("baseline_commit") == EXPECTED_LEDGER_BASELINE, "canonical ledger baseline drift", failures)
    require(ledger.get("entry_count") == 1078, "canonical ledger entry count drift", failures)
    require(ledger.get("ledger_sha256") == EXPECTED_LEDGER_SHA256, "canonical ledger identity drift", failures)
    require(ledger.get("canonical_fingerprint_count") == 1078 and ledger.get("canonical_fingerprint_missing_count") == 0, "canonical fingerprint closure drift", failures)
    require((ledger.get("blocking_reason_counts") or {}) == {}, "corpus-facing ledger blockers reappeared", failures)
    grouping = ledger.get("global_recording_group_resolution") or {}
    require(grouping.get("status") == "PASS", "global recording-group resolution not PASS", failures)
    require(grouping.get("fallback_asset_count_after") == 0, "fallback grouping closure regressed", failures)
    require(grouping.get("global_acoustic_component_count") == 17, "global acoustic component count drift", failures)
    require(grouping.get("members_reassigned_to_global_acoustic_component") == 97, "global component membership drift", failures)
    require(grouping.get("content_deleted") is False and grouping.get("content_merge_performed") is False, "grouping must not merge/delete content", failures)

    expected_positive = {"FIRE_ALARM": 9, "GLASS_SHATTER": 304, "SIREN": 173, "TIRE_SQUEAL": 11, "VEHICLE_HORN": 245}
    expected_hn = {"FIRE_ALARM": 34, "GLASS_SHATTER": 401, "SIREN": 32, "TIRE_SQUEAL": 0, "VEHICLE_HORN": 0}
    expected_hn_sources = {"FIRE_ALARM": 1, "GLASS_SHATTER": 1, "SIREN": 1, "TIRE_SQUEAL": 0, "VEHICLE_HORN": 0}
    require(ledger.get("positive_counts") == expected_positive, "positive corpus counts drift", failures)
    require(ledger.get("hard_negative_counts") == expected_hn, "hard-negative corpus counts drift", failures)
    require(ledger.get("hard_negative_underlying_source_family_counts") == expected_hn_sources, "hard-negative source-family counts drift", failures)

    # Structural nodes now closed.
    require(dedup.get("status") == "PASS" and dedup.get("gap_codes") == [], "global dedup must remain PASS", failures)
    require(group_audit.get("status") == "PASS" and group_audit.get("gap_codes") == [], "recording-family audit must remain PASS", failures)
    require(split.get("status") == "PASS" and split.get("gap_codes") == [], "split integrity must remain PASS", failures)
    require(split.get("original_split_conflict_count") == 3, "audited split conflict count drift", failures)
    require(split.get("original_split_conflicts_quarantined") == 3, "all protected split conflicts must stay quarantined", failures)
    require(split.get("quarantined_asset_count") == 62, "quarantined split asset count drift", failures)

    # Final corpus/model gate stays fail-closed until coverage/freezes/repro close.
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-CORPUS-001", "OPEN"), "corpus certificate is not OPEN", failures)
    require(readiness.get("readiness_id") == "EMP-MK1-CORPUS-READINESS-001", "unexpected readiness id", failures)
    require(readiness.get("status") == "BLOCKED", "readiness must remain BLOCKED", failures)
    require(readiness.get("eligible_for_certificate_review") is False, "certificate review must remain ineligible", failures)
    require(readiness.get("modeling_allowed") is False, "modeling_allowed must remain false", failures)
    require(readiness.get("corpus_certificate", {}).get("status") == "OPEN", "readiness corpus certificate state drift", failures)
    require(readiness.get("evidence_identity_sha256") == EXPECTED_EVIDENCE_IDENTITY, "readiness identity drift", failures)
    require(set(readiness.get("gap_codes", [])) == EXPECTED_GAPS, "readiness gap-code set drift; re-audit required", failures)
    ledger_input = readiness.get("inputs", {}).get("canonical_ledger_summary", {})
    require(ledger_input.get("baseline_commit") == EXPECTED_LEDGER_BASELINE, "readiness ledger baseline drift", failures)
    require(ledger_input.get("entry_count") == 1078, "readiness ledger count drift", failures)
    require(ledger_input.get("ledger_sha256") == EXPECTED_LEDGER_SHA256, "readiness ledger identity drift", failures)
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
        require(node.get("present") is True, f"closure node missing: {key}", failures)
        require(node.get("pass") is expected_pass, f"closure node pass-state drift: {key}", failures)

    # Product-direction guardrail.
    joined = docs["state"] + "\n" + docs["cert_ledger"] + "\n" + docs["foundry_gates"] + "\n" + docs["doc_audit"]
    for marker in ("Benchmark A/B/C", "Event Engine", "Edge Agent", "MQTT", "real camera", "modeling_allowed", "hard-negative", "freeze #2"):
        require(marker.casefold() in joined.casefold(), f"product/closure marker missing: {marker}", failures)
    require("CORPUS-001" in joined, "corpus-to-model dependency missing", failures)

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
    print("documentation certificate: CERT-DOC-009")
    print("toolchain: CERT-MK1-DF-TOOLCHAIN-005 CANDIDATE")
    print("SONYC: CERT-MK1-DF-SONYC-001 CERTIFIED")
    print("canonical fingerprints: 1078/1078")
    print("ledger blockers: 0")
    print("global dedup: PASS")
    print("recording-family audit: PASS")
    print("split integrity: PASS / 3 groups quarantined / 62 assets")
    print("readiness gaps:", len(EXPECTED_GAPS))
    print("corpus certificate: OPEN")
    print("modeling_allowed: false")
    print("markdown corpus files:", len(md_files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
