from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

CERTIFICATE_SCHEMA_VERSION = "echo.cert.v1"
CORPUS_CERTIFICATE_ID = "CERT-MK1-DF-CORPUS-001"
CORPUS_CERTIFICATE_VERSION = "1.0.0"
READINESS_ID = "EMP-MK1-CORPUS-READINESS-001"
FREE_TIER_POLICY_ID = "ECHO-FREE-TIER-001"
CERTIFICATE_PATH = "MK1/mining-site/materialization/cert-mk1-df-corpus-001.json"
CERTIFICATE_ONLY_GAP = "CORPUS_CERTIFICATE_NOT_CERTIFIED"


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    unsigned = dict(payload)
    unsigned.pop("certificate_sha256", None)
    return json.dumps(
        unsigned,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def certificate_sha256(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_payload(payload)).hexdigest()


def validate_pre_certificate_readiness(readiness: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []

    if readiness.get("readiness_id") != READINESS_ID:
        failures.append("unexpected readiness_id")
    if readiness.get("eligible_for_certificate_review") is not True:
        failures.append("readiness is not eligible_for_certificate_review")
    if readiness.get("modeling_allowed") is not False:
        failures.append("pre-certificate readiness must keep modeling_allowed=false")
    if str(readiness.get("status", "")).upper() != "BLOCKED":
        failures.append("pre-certificate readiness must be BLOCKED")

    gaps = readiness.get("gap_codes")
    if gaps != [CERTIFICATE_ONLY_GAP]:
        failures.append(
            "the only remaining readiness gap must be CORPUS_CERTIFICATE_NOT_CERTIFIED"
        )

    identity = str(readiness.get("evidence_identity_sha256") or "")
    if len(identity) != 64:
        failures.append("readiness evidence_identity_sha256 is missing or malformed")

    certificate = readiness.get("corpus_certificate")
    if not isinstance(certificate, Mapping):
        failures.append("readiness corpus_certificate object is missing")
    else:
        if str(certificate.get("id") or "") != CORPUS_CERTIFICATE_ID:
            failures.append("unexpected corpus certificate id")
        if str(certificate.get("status") or "").upper() == "CERTIFIED":
            failures.append("pre-certificate readiness already claims CERTIFIED")

    nodes = readiness.get("closure_evidence_nodes")
    if not isinstance(nodes, Mapping) or not nodes:
        failures.append("closure evidence nodes are missing")
    else:
        for node, row in sorted(nodes.items()):
            if not isinstance(row, Mapping):
                failures.append(f"closure evidence node {node} is malformed")
                continue
            if row.get("present") is not True or row.get("pass") is not True:
                failures.append(f"closure evidence node {node} is not PASS")
            digest = str(row.get("sha256") or "")
            if len(digest) != 64:
                failures.append(f"closure evidence node {node} lacks a sha256")

    inputs = readiness.get("inputs")
    if not isinstance(inputs, Mapping):
        failures.append("readiness inputs are missing")
    else:
        for key in ("canonical_ledger_summary", "coverage_policy"):
            row = inputs.get(key)
            if not isinstance(row, Mapping) or len(str(row.get("sha256") or "")) != 64:
                failures.append(f"readiness input {key} lacks a sha256")

    return failures


def build_corpus_certificate(
    *,
    readiness: Mapping[str, Any],
    git_commit: str,
    generated_at_utc: str,
    free_tier_policy_sha256: str,
    github_run_id: str | None = None,
) -> dict[str, Any]:
    failures = validate_pre_certificate_readiness(readiness)
    if failures:
        raise ValueError("; ".join(failures))

    nodes = readiness["closure_evidence_nodes"]
    evidence = [
        {
            "id": node,
            "path": f"MK1/mining-site/materialization/{row['filename']}",
            "sha256": row["sha256"],
            "result": "PASS",
        }
        for node, row in sorted(nodes.items())
    ]

    payload: dict[str, Any] = {
        "schema_version": CERTIFICATE_SCHEMA_VERSION,
        "artifact_id": CORPUS_CERTIFICATE_ID,
        "artifact_version": CORPUS_CERTIFICATE_VERSION,
        "status": "CERTIFIED",
        "scope": "MK1 release_safe frozen acoustic corpus",
        "documentation": [
            {"certificate": "CERT-DOC-005"},
            {"path": "governance/CERTIFICATION-DAG.md"},
            {"path": "MK1/build/data-foundry/CORPUS-SOLIDITY-GATE.md"},
            {"path": "MK1/build/data-foundry/CORPUS-FREEZE.md"},
        ],
        "free_tier_boundary": {
            "policy_id": FREE_TIER_POLICY_ID,
            "policy_sha256": free_tier_policy_sha256,
            "result": "PASS",
        },
        "inputs": {
            "corpus_readiness": {
                "id": READINESS_ID,
                "evidence_identity_sha256": readiness["evidence_identity_sha256"],
                "eligible_for_certificate_review": True,
            },
            "canonical_ledger_summary": dict(
                readiness["inputs"]["canonical_ledger_summary"]
            ),
            "coverage_policy": dict(readiness["inputs"]["coverage_policy"]),
        },
        "outputs": [{"path": CERTIFICATE_PATH}],
        "criteria": [
            {
                "id": "CORPUS_READINESS_ELIGIBLE",
                "result": "PASS",
            },
            {
                "id": "ALL_CLOSURE_EVIDENCE_PASS",
                "result": "PASS",
            },
            {
                "id": "NO_OPEN_GAPS_EXCEPT_CERTIFICATE",
                "result": "PASS",
            },
            {
                "id": "ECHO_FREE_TIER_001",
                "result": "PASS",
            },
        ],
        "provenance": {
            "git_commit": git_commit,
            "generated_at_utc": generated_at_utc,
            "github_run_id": github_run_id,
        },
        "evidence": evidence,
        "non_claims": [
            "Does not certify a model winner, thresholds, field performance, distance/SNR envelope, or real-camera operation.",
            "Does not broaden release_safe licensing beyond the exact admitted corpus identity bound by the evidence hashes.",
        ],
        "invalidates_if": [
            "canonical ledger identity changes",
            "coverage policy changes",
            "any dedup, recording-family, split, coverage, freeze, or reproducibility evidence changes",
            "source, asset, rights, mapping, grouping, fingerprint, or freeze semantics change",
            "ECHO-FREE-TIER-001 is violated",
            "a required documentation ancestor becomes stale or invalidated",
        ],
        "hash_contract": "certificate_sha256 is SHA-256 over canonical JSON of this object with certificate_sha256 omitted",
    }
    payload["certificate_sha256"] = certificate_sha256(payload)
    return payload


def validate_corpus_certificate(
    certificate: Mapping[str, Any], *, evidence_identity_sha256: str
) -> list[str]:
    failures: list[str] = []

    if certificate.get("schema_version") != CERTIFICATE_SCHEMA_VERSION:
        failures.append("unexpected certificate schema_version")
    if certificate.get("artifact_id") != CORPUS_CERTIFICATE_ID:
        failures.append("unexpected certificate artifact_id")
    if str(certificate.get("status") or "").upper() != "CERTIFIED":
        failures.append("certificate status is not CERTIFIED")

    boundary = certificate.get("free_tier_boundary")
    if not isinstance(boundary, Mapping):
        failures.append("free_tier_boundary is missing")
    else:
        if boundary.get("policy_id") != FREE_TIER_POLICY_ID:
            failures.append("unexpected free-tier policy id")
        if str(boundary.get("result") or "").upper() != "PASS":
            failures.append("free-tier boundary did not PASS")
        if len(str(boundary.get("policy_sha256") or "")) != 64:
            failures.append("free-tier policy sha256 is missing or malformed")

    inputs = certificate.get("inputs")
    readiness_input = inputs.get("corpus_readiness") if isinstance(inputs, Mapping) else None
    if not isinstance(readiness_input, Mapping):
        failures.append("certificate readiness input is missing")
    elif readiness_input.get("evidence_identity_sha256") != evidence_identity_sha256:
        failures.append("certificate evidence identity does not match current readiness")

    criteria = certificate.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        failures.append("certificate criteria are missing")
    else:
        if any(
            not isinstance(row, Mapping)
            or str(row.get("result") or "").upper() != "PASS"
            for row in criteria
        ):
            failures.append("certificate contains a non-PASS criterion")

    claimed_hash = str(certificate.get("certificate_sha256") or "")
    if len(claimed_hash) != 64:
        failures.append("certificate_sha256 is missing or malformed")
    elif claimed_hash != certificate_sha256(certificate):
        failures.append("certificate_sha256 does not match certificate payload")

    return failures


def apply_corpus_certificate(
    readiness: dict[str, Any], certificate: Mapping[str, Any]
) -> dict[str, Any]:
    result = dict(readiness)
    failures = validate_corpus_certificate(
        certificate,
        evidence_identity_sha256=str(readiness.get("evidence_identity_sha256") or ""),
    )

    if failures:
        gaps = list(result.get("gap_codes") or [])
        if "CORPUS_CERTIFICATE_INVALID" not in gaps:
            gaps.append("CORPUS_CERTIFICATE_INVALID")
        result["gap_codes"] = sorted(dict.fromkeys(gaps))
        result["corpus_certificate"] = {
            "id": CORPUS_CERTIFICATE_ID,
            "status": "INVALIDATED",
            "validation_failures": failures,
        }
        result["modeling_allowed"] = False
        result["status"] = "BLOCKED"
        result["next_authorized_stage"] = "CORPUS_FOUNDRY_CLOSURE"
        return result

    gaps = [
        gap
        for gap in list(result.get("gap_codes") or [])
        if gap != CERTIFICATE_ONLY_GAP
    ]
    result["gap_codes"] = sorted(dict.fromkeys(gaps))
    result["corpus_certificate"] = {
        "id": CORPUS_CERTIFICATE_ID,
        "status": "CERTIFIED",
        "certificate_sha256": certificate["certificate_sha256"],
        "evidence_identity_sha256": evidence_identity_sha256_from_certificate(certificate),
    }
    result["modeling_allowed"] = bool(
        result.get("eligible_for_certificate_review") and not result["gap_codes"]
    )
    result["status"] = "READY" if result["modeling_allowed"] else "BLOCKED"
    result["next_authorized_stage"] = (
        "BENCHMARK_A_B_C" if result["modeling_allowed"] else "CORPUS_FOUNDRY_CLOSURE"
    )
    return result


def evidence_identity_sha256_from_certificate(certificate: Mapping[str, Any]) -> str:
    inputs = certificate.get("inputs")
    if not isinstance(inputs, Mapping):
        return ""
    readiness = inputs.get("corpus_readiness")
    if not isinstance(readiness, Mapping):
        return ""
    return str(readiness.get("evidence_identity_sha256") or "")
