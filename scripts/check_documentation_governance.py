#!/usr/bin/env python3
"""Fail closed when ECHO documentation/certification truth drifts.

DOC-015 governs the corpus-certificate handoff state. The checker freezes the
current semantic corpus identity, the certificate lineage, empirical stop-lines,
and the rule that certificate infrastructure may exist without manufacturing a
corpus certificate while coverage remains incomplete.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROMISE = "Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial"
CURRENT_DOC_CERT = "CERT-DOC-015"
EXPECTED_MD_COUNT = 221
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

FILES = {
    "charter": ROOT / "PROJECT-CHARTER.md",
    "state": ROOT / "CURRENT-STATE.md",
    "doc_standard": ROOT / "governance/DOCUMENTATION-STANDARD.md",
    "doc_coverage": ROOT / "governance/DOCUMENTATION-COVERAGE.md",
    "doc_audit": ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-16-CORPUS-HANDOFF-015.md",
    "cert_ledger": ROOT / "governance/CERTIFICATION-LEDGER.md",
    "free_tier": ROOT / "governance/FREE-TIER-BOUNDARY.md",
    "foundry_gates": ROOT / "MK1/build/data-foundry/FOUNDRY-GATES.md",
    "handoff": ROOT / "MK1/build/data-foundry/CORPUS-CERTIFICATE-HANDOFF.md",
    "toolchain005": ROOT / "MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-005.md",
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


def read_text(name: str) -> str:
    return FILES[name].read_text(encoding="utf-8")


def read_json(name: str) -> dict[str, Any]:
    value = json.loads(read_text(name))
    if not isinstance(value, dict):
        raise ValueError(f"{name}: expected JSON object")
    return value


def ledger_state(body: str, cert_id: str, state: str) -> bool:
    return re.search(rf"\|\s*{re.escape(cert_id)}\s*\|.*\|\s*{re.escape(state)}\s*\|", body) is not None


def semantic_identity(readiness: dict[str, Any]) -> str:
    material = readiness.get("evidence_identity_material")
    if not isinstance(material, dict):
        return ""
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    failures: list[str] = []
    for name, path in FILES.items():
        require(path.is_file(), f"missing required authority: {name} -> {path.relative_to(ROOT)}", failures)
    if failures:
        return fail(failures)

    json_names = {"near_policy", "sonyc_cert", "ledger_summary", "dedup", "group_audit", "split", "coverage", "readiness", "freeze1", "freeze2", "repro"}
    docs = {name: read_text(name) for name in FILES if name not in json_names}
    near = read_json("near_policy")
    sonyc = read_json("sonyc_cert")
    ledger = read_json("ledger_summary")
    dedup = read_json("dedup")
    family = read_json("group_audit")
    split = read_json("split")
    coverage = read_json("coverage")
    readiness = read_json("readiness")
    freeze1 = read_json("freeze1")
    freeze2 = read_json("freeze2")
    repro = read_json("repro")

    # Project-wide authorities.
    require(PROMISE in docs["charter"] and PROMISE in docs["state"], "immutable promise drift", failures)
    require("FROZEN_DOCUMENTATION_GOVERNANCE" in docs["doc_standard"], "documentation governance is not frozen", failures)
    require("ECHO-FREE-TIER-001" in docs["doc_standard"], "documentation standard lost free-tier ancestor", failures)
    require("FROZEN_GLOBAL_POLICY" in docs["free_tier"] and "0 USD" in docs["free_tier"], "free-tier invariant drift", failures)

    # DOC-015 and certificate lineage.
    require("**Current certificate:** `CERT-DOC-015`" in docs["doc_coverage"], "DOCUMENTATION-COVERAGE does not name DOC-015 current", failures)
    require("**Documentation certificate:** `CERT-DOC-015`" in docs["state"], "CURRENT-STATE does not name DOC-015", failures)
    require("**Certificate:** `CERT-DOC-015`" in docs["doc_audit"] and "**Status:** `CERTIFIED`" in docs["doc_audit"], "DOC-015 audit is not certified", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-015", "CERTIFIED"), "CERT-DOC-015 not CERTIFIED in ledger", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-DOC-001..014", "INVALIDATED"), "historical DOC lineage not invalidated through DOC-014", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-TOOLCHAIN-004", "INVALIDATED"), "TOOLCHAIN-004 must remain invalidated", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-TOOLCHAIN-005", "CERTIFIED"), "TOOLCHAIN-005 must be CERTIFIED", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-HANDOFF-001", "CERTIFIED"), "HANDOFF-001 must be CERTIFIED", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-SONYC-001", "CERTIFIED"), "SONYC-001 must remain CERTIFIED", failures)
    require(ledger_state(docs["cert_ledger"], "CERT-MK1-DF-CORPUS-001", "OPEN"), "corpus certificate must remain OPEN while empirical gaps remain", failures)
    require("CERT-MK1-DF-TOOLCHAIN-005         = CERTIFIED" in docs["state"], "CURRENT-STATE lost TOOLCHAIN-005 certification", failures)
    require("CERT-MK1-DF-HANDOFF-001           = CERTIFIED" in docs["state"], "CURRENT-STATE lost HANDOFF-001 certification", failures)
    require("CERT-MK1-DF-TOOLCHAIN-005" in docs["toolchain005"] and "**Status:** `CERTIFIED`" in docs["toolchain005"], "TOOLCHAIN-005 certificate file invalid", failures)
    require("CERT-MK1-DF-HANDOFF-001" in docs["handoff"] and "**Status:** `CERTIFIED`" in docs["handoff"], "HANDOFF-001 authority invalid", failures)

    # Scoped SONYC certificate remains pinned.
    require(sonyc.get("artifact_id") == "CERT-MK1-DF-SONYC-001" and sonyc.get("status") == "CERTIFIED", "SONYC certificate drift", failures)
    require(sonyc.get("implementation_baseline") == "ab8c47ba6aabb25390644954a2a06945ca7a81bb", "SONYC implementation baseline drift", failures)
    require(sonyc.get("materialization_run_id") == 34922010537, "SONYC run drift", failures)
    require(sonyc.get("durable_evidence_commit") == "78fc019839f1c9dad1a58a70d439605d887361d7", "SONYC durable evidence drift", failures)
    require((sonyc.get("free_tier_boundary") or {}).get("result") == "PASS", "SONYC free-tier result drift", failures)

    # Near-duplicate policy remains screen -> confirm -> group.
    comparison = near.get("comparison") or {}
    require(float(comparison.get("candidate_max_distance", -1)) == 0.02, "candidate screening threshold drift", failures)
    require(float(comparison.get("confirmed_group_max_distance", -1)) == 0.002, "confirmed grouping threshold drift", failures)
    require(float(comparison.get("confirmed_group_max_relative_sample_count_delta", -1)) == 0.01, "confirmed length compatibility drift", failures)
    require(comparison.get("automatic_merge") is False, "automatic near-duplicate merge must remain false", failures)
    require(comparison.get("action") == "SCREEN_THEN_CONFIRM_FOR_SPLIT_PROTECTION", "near-duplicate action drift", failures)
    require("review-only screening edges never union components" in str(comparison.get("transitive_rule") or ""), "screen-only transitive stop-line drift", failures)

    # Canonical semantic truth; baseline is provenance only.
    baseline = str(ledger.get("baseline_commit") or "")
    require(re.fullmatch(r"[0-9a-f]{40}", baseline) is not None, "ledger provenance baseline malformed", failures)
    require(ledger.get("entry_count") == 1141, "ledger entry count drift", failures)
    require(ledger.get("ledger_sha256") == EXPECTED_LEDGER_SHA256, "semantic ledger identity drift", failures)
    require(ledger.get("canonical_fingerprint_count") == 1141 and ledger.get("canonical_fingerprint_missing_count") == 0, "fingerprint closure drift", failures)
    require((ledger.get("blocking_reason_counts") or {}) == {}, "ledger blockers reappeared", failures)
    grouping = ledger.get("global_recording_group_resolution") or {}
    require(grouping.get("status") == "PASS" and grouping.get("fallback_asset_count_after") == 0, "global grouping closure drift", failures)
    require(grouping.get("global_acoustic_component_count") == 2 and grouping.get("members_reassigned_to_global_acoustic_component") == 4, "global acoustic component drift", failures)
    require(grouping.get("near_duplicate_candidate_edge_count") == 855, "candidate-edge count drift", failures)
    require(grouping.get("confirmed_near_duplicate_grouping_edge_count") == 2, "confirmed grouping-edge count drift", failures)
    require(grouping.get("review_only_near_duplicate_edge_count") == 853, "review-only edge count drift", failures)
    require(grouping.get("candidate_edges_rejected_by_length_count") == 835, "length-rejected edge count drift", failures)
    require(grouping.get("content_deleted") is False and grouping.get("content_merge_performed") is False, "grouping must not merge/delete content", failures)
    require(ledger.get("positive_counts") == {"FIRE_ALARM": 19, "GLASS_SHATTER": 303, "SIREN": 169, "TIRE_SQUEAL": 14, "VEHICLE_HORN": 235}, "positive counts drift", failures)
    require(ledger.get("hard_negative_counts") == {"FIRE_ALARM": 202, "GLASS_SHATTER": 440, "SIREN": 235, "TIRE_SQUEAL": 25, "VEHICLE_HORN": 142}, "hard-negative counts drift", failures)

    # Structural closure.
    require(dedup.get("schema_version") == "echo.global-dedup-audit.v2" and dedup.get("status") == "PASS" and dedup.get("gap_codes") == [], "global dedup not PASS", failures)
    require(dedup.get("ledger_sha256") == EXPECTED_COVERAGE_LEDGER_SHA256, "dedup material-ledger identity drift", failures)
    require(dedup.get("fingerprinted_asset_count") == 1141 and dedup.get("missing_fingerprint_count") == 0, "dedup fingerprint coverage drift", failures)
    require(dedup.get("confirmed_near_duplicate_cross_group_count") == 0, "confirmed near-duplicate cross-group conflict reappeared", failures)
    require(dedup.get("exact_media_duplicate_group_count") == 0 and dedup.get("exact_canonical_pcm_duplicate_group_count") == 0, "exact duplicate groups reappeared", failures)
    require(family.get("schema_version") == "echo.recording-family-audit.v2" and family.get("status") == "PASS" and family.get("gap_codes") == [], "recording-family audit not PASS", failures)
    require(family.get("recording_family_count") == 1075 and family.get("missing_recording_group_count") == 0, "recording-family closure drift", failures)
    require(split.get("status") == "PASS" and split.get("gap_codes") == [], "split integrity not PASS", failures)
    require(split.get("original_split_conflict_count") == 0 and split.get("quarantined_asset_count") == 0, "split conflict/quarantine drift", failures)
    require(split.get("eligible_asset_count") == 1141 and split.get("ready_candidate_asset_count") == 1141, "split eligible count drift", failures)
    require(split.get("split_asset_counts") == {"test": 463, "train": 439, "validation": 239}, "global split counts drift", failures)

    # Empirical coverage truth remains unchanged by certificate infrastructure.
    require(coverage.get("status") == "FAIL", "coverage status changed; fresh documentation audit required", failures)
    require(coverage.get("ledger_sha256") == EXPECTED_COVERAGE_LEDGER_SHA256, "coverage ledger identity drift", failures)
    require(set(coverage.get("gap_codes") or []) == EXPECTED_COVERAGE_GAPS and len(coverage.get("gap_codes") or []) == 16, "coverage gap set drift", failures)
    require(coverage.get("development_asset_count") == 1141 and coverage.get("quarantined_split_conflict_asset_count") == 0, "coverage development/quarantine drift", failures)
    require((coverage.get("asset_quality") or {}) == EXPECTED_QUALITY, "asset-quality stop-lines drift", failures)
    background = coverage.get("background") or {}
    require((background.get("asset_count"), background.get("independent_group_count"), background.get("source_count")) == (428, 385, 4), "background closure drift", failures)
    classes = coverage.get("classes") or {}
    fire = classes.get("FIRE_ALARM") or {}
    glass = classes.get("GLASS_SHATTER") or {}
    tire = classes.get("TIRE_SQUEAL") or {}
    require((fire.get("asset_count"), fire.get("independent_group_count"), fire.get("source_count")) == (19, 16, 3), "FIRE coverage drift", failures)
    require(fire.get("split_assets") == {"test": 0, "train": 17, "validation": 2}, "FIRE split drift", failures)
    require((glass.get("asset_count"), glass.get("independent_group_count"), glass.get("source_count"), glass.get("max_single_source_fraction")) == (303, 287, 4, 0.924092), "GLASS coverage/concentration drift", failures)
    require((tire.get("asset_count"), tire.get("independent_group_count"), tire.get("source_count")) == (14, 10, 2), "TIRE coverage drift", failures)
    require(tire.get("split_assets") == {"test": 3, "train": 11, "validation": 0}, "TIRE split drift", failures)

    # Freeze/reproducibility remain blocked only by empirical coverage.
    require(freeze1.get("status") == "FAIL" and freeze1.get("gap_codes") == ["UPSTREAM_COVERAGE_NOT_PASS"], "freeze #1 drift", failures)
    require(freeze2.get("status") == "FAIL" and freeze2.get("gap_codes") == ["UPSTREAM_COVERAGE_NOT_PASS"], "freeze #2 drift", failures)
    require(repro.get("status") == "FAIL" and repro.get("gap_codes") == ["UPSTREAM_FREEZE_NOT_ELIGIBLE"], "reproducibility drift", failures)

    # Readiness v2: semantic identity stable, certificate remains OPEN today.
    require(readiness.get("schema_version") == "echo.corpus-closure-readiness.v2", "readiness v2 not active", failures)
    require(readiness.get("readiness_id") == "EMP-MK1-CORPUS-READINESS-001", "readiness id drift", failures)
    require(readiness.get("status") == "BLOCKED" and readiness.get("modeling_allowed") is False, "readiness/modeling lock drift", failures)
    require(readiness.get("eligible_for_certificate_review") is False, "readiness unexpectedly certificate-eligible", failures)
    require(readiness.get("next_authorized_stage") == "CORPUS_FOUNDRY_CLOSURE", "next authorized stage drift", failures)
    require((readiness.get("corpus_certificate") or {}).get("status") == "OPEN", "corpus certificate must remain OPEN", failures)
    require(set(readiness.get("gap_codes") or []) == EXPECTED_READINESS_GAPS, "readiness gap set drift", failures)
    ri = (readiness.get("inputs") or {}).get("canonical_ledger_summary") or {}
    require(ri.get("baseline_commit") == baseline, "readiness provenance baseline disagreement", failures)
    require(ri.get("ledger_sha256") == EXPECTED_LEDGER_SHA256 and ri.get("entry_count") == 1141, "readiness ledger binding drift", failures)
    require("execution provenance" in str(ri.get("provenance_note") or ""), "readiness lost provenance boundary note", failures)
    material = readiness.get("evidence_identity_material") or {}
    require(material.get("canonical_ledger_semantic_sha256") == EXPECTED_LEDGER_SHA256, "readiness semantic ledger identity drift", failures)
    require(material.get("coverage_policy_sha256") == EXPECTED_POLICY_SHA256, "readiness policy identity drift", failures)
    closure_hashes = material.get("closure_evidence_sha256") or {}
    for node, row in (readiness.get("closure_evidence_nodes") or {}).items():
        require(closure_hashes.get(node) == row.get("sha256"), f"readiness closure hash mismatch: {node}", failures)
    computed_identity = semantic_identity(readiness)
    require(computed_identity == EXPECTED_EVIDENCE_IDENTITY and readiness.get("evidence_identity_sha256") == computed_identity, "readiness semantic identity drift", failures)

    # Certificate handoff stop-line must be explicit in all governing docs.
    for name in ("state", "doc_coverage", "cert_ledger", "doc_audit", "handoff", "foundry_gates"):
        body = docs[name]
        require("CERT-MK1-DF-CORPUS-001" in body, f"{name} lost corpus certificate stop-line", failures)
        require("Benchmark A/B/C" in body, f"{name} lost benchmark gate", failures)
    require("gap_codes = [CORPUS_CERTIFICATE_NOT_CERTIFIED]" in docs["handoff"], "handoff lost exact pre-certificate condition", failures)
    require("issuance is a no-op" in docs["handoff"].lower(), "handoff lost fail-closed no-op rule", failures)
    require("modeling_allowed = false" in docs["state"], "CURRENT-STATE lost modeling lock", failures)

    # Documentation inventory itself is governed.
    markdown_files = sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)
    require(len(markdown_files) == EXPECTED_MD_COUNT, f"Markdown corpus count drift: expected {EXPECTED_MD_COUNT}, got {len(markdown_files)}", failures)
    for path in markdown_files:
        body = path.read_text(encoding="utf-8")
        if "<<<<<<< " in body or "\n>>>>>>> " in body:
            failures.append(f"merge-conflict marker detected in {path.relative_to(ROOT)}")

    if failures:
        return fail(failures)

    print("DOCUMENTATION GOVERNANCE: PASS")
    print(f" certificate={CURRENT_DOC_CERT} markdown_files={len(markdown_files)}")
    print(" toolchain=CERTIFIED handoff=CERTIFIED corpus=OPEN")
    print(f" semantic_ledger={EXPECTED_LEDGER_SHA256}")
    print(f" readiness_identity={computed_identity}")
    print(f" execution_baseline={baseline} (provenance only)")
    print(" dedup=PASS family=PASS split=PASS quarantine=0")
    print(f" coverage_gaps={len(EXPECTED_COVERAGE_GAPS)} modeling_allowed=false")
    return 0


def fail(failures: list[str]) -> int:
    print("DOCUMENTATION GOVERNANCE: FAIL")
    for failure in failures:
        print(" -", failure)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
