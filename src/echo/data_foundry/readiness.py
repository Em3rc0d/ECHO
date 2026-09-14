from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "echo.corpus-closure-readiness.v1"
READINESS_ID = "EMP-MK1-CORPUS-READINESS-001"
CORPUS_CERTIFICATE_ID = "CERT-MK1-DF-CORPUS-001"

REQUIRED_TARGETS = (
    "GLASS_SHATTER",
    "SIREN",
    "FIRE_ALARM",
    "VEHICLE_HORN",
    "TIRE_SQUEAL",
)

REQUIRED_EVIDENCE_NODES = {
    "global_dedup_audit": "global-dedup-audit.json",
    "recording_family_audit": "recording-family-audit.json",
    "split_integrity": "split-integrity.json",
    "coverage_gate": "coverage-gate.json",
    "freeze_1_validation": "corpus-freeze-1.validation.json",
    "freeze_2_validation": "corpus-freeze-2.validation.json",
    "reproducibility": "corpus-reproducibility.json",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def _certificate(summary: dict[str, Any]) -> dict[str, str]:
    raw = summary.get("corpus_certificate")
    if not isinstance(raw, dict):
        raw = summary.get("certificate")
    if not isinstance(raw, dict):
        raw = {}
    return {
        "id": str(raw.get("id") or CORPUS_CERTIFICATE_ID),
        "status": str(raw.get("status") or "OPEN").upper(),
    }


def _int_mapping(summary: dict[str, Any], key: str) -> dict[str, int]:
    raw = summary.get(key)
    if not isinstance(raw, dict):
        return {}
    result: dict[str, int] = {}
    for name, value in raw.items():
        try:
            result[str(name)] = int(value)
        except (TypeError, ValueError):
            continue
    return result


def _artifact_pass(payload: dict[str, Any] | None) -> bool:
    if not payload:
        return False
    status = str(payload.get("status", "")).upper()
    if status not in {"PASS", "CERTIFIED", "IDENTICAL"}:
        return False
    gaps = payload.get("gap_codes")
    return gaps in (None, [])


def evaluate_readiness(
    *,
    ledger_summary: dict[str, Any],
    coverage_policy: dict[str, Any],
    evidence_artifacts: dict[str, dict[str, Any] | None],
    evidence_hashes: dict[str, str | None],
) -> dict[str, Any]:
    profile = coverage_policy.get("profiles", {}).get("release_safe", {})
    target_policy = profile.get("target_labels", {})
    positives = _int_mapping(ledger_summary, "positive_counts")
    hard_negatives = _int_mapping(ledger_summary, "hard_negative_counts")
    hard_negative_sources = _int_mapping(
        ledger_summary, "hard_negative_underlying_source_family_counts"
    )
    positive_sources = _int_mapping(
        ledger_summary, "positive_underlying_source_family_counts"
    )
    blockers = _int_mapping(ledger_summary, "blocking_reason_counts")
    cert = _certificate(ledger_summary)

    target_readiness: dict[str, Any] = {}
    gap_codes: list[str] = []

    hard_negative_policy = profile.get("hard_negatives", {}).get("per_target", {})
    for target in REQUIRED_TARGETS:
        cfg = target_policy.get(target, {}) if isinstance(target_policy, dict) else {}
        hn_cfg = (
            hard_negative_policy.get(target, {})
            if isinstance(hard_negative_policy, dict)
            else {}
        )
        current = int(positives.get(target, 0))
        min_assets = int(cfg.get("min_assets", 0) or 0)
        source_count = int(positive_sources.get(target, 0))
        min_sources = int(cfg.get("min_sources", 0) or 0)
        hn_current = int(hard_negatives.get(target, 0))
        hn_min = int(hn_cfg.get("min_assets", 0) or 0)
        hn_source_count = int(hard_negative_sources.get(target, 0))
        hn_min_sources = int(hn_cfg.get("min_sources", 0) or 0)

        if current < min_assets:
            gap_codes.append(f"{target}_ASSETS_{current}_LT_{min_assets}")
        if source_count < min_sources:
            gap_codes.append(
                f"{target}_UNDERLYING_SOURCES_{source_count}_LT_{min_sources}"
            )
        if hn_current < hn_min:
            gap_codes.append(f"{target}_HARD_NEGATIVES_{hn_current}_LT_{hn_min}")
        if hn_source_count < hn_min_sources:
            gap_codes.append(
                f"{target}_HARD_NEGATIVE_SOURCES_{hn_source_count}_LT_{hn_min_sources}"
            )

        target_readiness[target] = {
            "positive_assets_pre_final_dedup": current,
            "positive_assets_floor": min_assets,
            "positive_underlying_source_families": source_count,
            "positive_source_floor": min_sources,
            "hard_negative_assets_pre_final_dedup": hn_current,
            "hard_negative_assets_floor": hn_min,
            "hard_negative_underlying_source_families": hn_source_count,
            "hard_negative_source_floor": hn_min_sources,
            "precheck_status": (
                "PASS"
                if (
                    current >= min_assets
                    and source_count >= min_sources
                    and hn_current >= hn_min
                    and hn_source_count >= hn_min_sources
                )
                else "FAIL"
            ),
            "scope_note": (
                "Precheck only; final coverage also requires groups, duration, per-split "
                "floors, source concentration, quality, rights and duplicate controls."
            ),
        }

    for reason, count in sorted(blockers.items()):
        if count > 0:
            gap_codes.append(f"LEDGER_{reason}_{count}")

    if int(ledger_summary.get("canonical_fingerprint_missing_count", 0) or 0) > 0:
        gap_codes.append("CANONICAL_FINGERPRINT_COVERAGE_INCOMPLETE")

    evidence_status: dict[str, Any] = {}
    for node, filename in REQUIRED_EVIDENCE_NODES.items():
        payload = evidence_artifacts.get(node)
        passed = _artifact_pass(payload)
        evidence_status[node] = {
            "filename": filename,
            "present": payload is not None,
            "status": payload.get("status") if payload else "MISSING",
            "sha256": evidence_hashes.get(node),
            "pass": passed,
        }
        if not passed:
            gap_codes.append(f"{node.upper()}_NOT_PASS")

    coverage_gate = evidence_artifacts.get("coverage_gate")
    if coverage_gate is None:
        gap_codes.append("COVERAGE_GATE_MISSING")
    else:
        if str(coverage_gate.get("status", "")).upper() != "PASS":
            gap_codes.append("COVERAGE_GATE_STATUS_NOT_PASS")
        gate_gaps = coverage_gate.get("gap_codes")
        if gate_gaps != []:
            gap_codes.append("COVERAGE_GATE_GAP_CODES_NOT_EMPTY")

    if cert["status"] != "CERTIFIED":
        gap_codes.append("CORPUS_CERTIFICATE_NOT_CERTIFIED")

    gap_codes = sorted(dict.fromkeys(gap_codes))

    closure_inputs_pass = all(item["pass"] for item in evidence_status.values())
    ledger_preconditions_pass = (
        not blockers
        and int(ledger_summary.get("canonical_fingerprint_missing_count", 0) or 0) == 0
        and all(row["precheck_status"] == "PASS" for row in target_readiness.values())
    )
    eligible_for_certificate_review = closure_inputs_pass and ledger_preconditions_pass

    modeling_allowed = (
        eligible_for_certificate_review
        and cert["status"] == "CERTIFIED"
        and not gap_codes
    )

    identity_material = {
        "ledger_sha256": evidence_hashes.get("canonical_ledger_summary"),
        "coverage_policy_sha256": evidence_hashes.get("coverage_policy"),
        "closure_evidence_sha256": {
            node: evidence_hashes.get(node) for node in sorted(REQUIRED_EVIDENCE_NODES)
        },
    }
    identity = hashlib.sha256(
        json.dumps(identity_material, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()

    return {
        "schema_version": SCHEMA_VERSION,
        "readiness_id": READINESS_ID,
        "profile": "release_safe",
        "status": "READY" if modeling_allowed else "BLOCKED",
        "modeling_allowed": modeling_allowed,
        "eligible_for_certificate_review": eligible_for_certificate_review,
        "release_law": (
            "NO CERT-MK1-DF-CORPUS-001 = NO Benchmark A/B/C, no YAMNet/PANNs/CNN, "
            "no EMP-MODEL-001, no threshold calibration, no replay pipeline, no real camera."
        ),
        "corpus_certificate": cert,
        "evidence_identity_sha256": identity,
        "inputs": {
            "canonical_ledger_summary": {
                "sha256": evidence_hashes.get("canonical_ledger_summary"),
                "baseline_commit": ledger_summary.get("baseline_commit"),
                "ledger_sha256": ledger_summary.get("ledger_sha256"),
                "entry_count": ledger_summary.get("entry_count"),
            },
            "coverage_policy": {
                "sha256": evidence_hashes.get("coverage_policy"),
                "policy_id": coverage_policy.get("policy_id"),
                "schema_version": coverage_policy.get("schema_version"),
            },
        },
        "target_readiness": target_readiness,
        "ledger_blocking_reason_counts": blockers,
        "closure_evidence_nodes": evidence_status,
        "gap_codes": gap_codes,
        "next_authorized_stage": (
            "BENCHMARK_A_B_C" if modeling_allowed else "CORPUS_FOUNDRY_CLOSURE"
        ),
    }
