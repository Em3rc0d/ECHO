from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

CERTIFICATE_SCHEMA_VERSION = "echo.corpus-certificate.v2"
CORPUS_CERTIFICATE_ID = "CERT-MK1-DF-CORPUS-001"
CORPUS_CERTIFICATE_VERSION = "1.0.0"
READINESS_ID = "EMP-MK1-CORPUS-READINESS-001"
DATASET_EMPIRICAL_ID = "EMP-DATASET-001"
DATA_QUALITY_EMPIRICAL_ID = "EMP-DATA-QUALITY-001"
TOOLCHAIN_CERTIFICATE_ID = "CERT-MK1-DF-TOOLCHAIN-005"
DOCUMENTATION_CERTIFICATE_ID = "CERT-DOC-015"
FREE_TIER_POLICY_ID = "ECHO-FREE-TIER-001"
CERTIFICATE_PATH = "MK1/mining-site/materialization/cert-mk1-df-corpus-001.json"
TOOLCHAIN_CERTIFICATE_PATH = "MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-005.md"
DOCUMENTATION_CERTIFICATE_PATH = "governance/DOCUMENTATION-AUDIT-2026-09-16-CORPUS-HANDOFF-015.md"
FREE_TIER_POLICY_PATH = "configs/data_foundry/free_tier_boundary.v1.json"
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


def _is_sha256(value: Any) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(ch in "0123456789abcdef" for ch in text)


def _is_commit_sha(value: Any) -> bool:
    text = str(value or "")
    return len(text) == 40 and all(ch in "0123456789abcdef" for ch in text)


def validate_pre_certificate_readiness(readiness: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []

    if readiness.get("schema_version") != "echo.corpus-closure-readiness.v2":
        failures.append("pre-certificate readiness must use v2 semantic identity")
    if readiness.get("readiness_id") != READINESS_ID:
        failures.append("unexpected readiness_id")
    if readiness.get("eligible_for_certificate_review") is not True:
        failures.append("readiness is not eligible_for_certificate_review")
    if readiness.get("modeling_allowed") is not False:
        failures.append("pre-certificate readiness must keep modeling_allowed=false")
    if str(readiness.get("status", "")).upper() != "BLOCKED":
        failures.append("pre-certificate readiness must be BLOCKED")
    if readiness.get("next_authorized_stage") != "CORPUS_FOUNDRY_CLOSURE":
        failures.append("pre-certificate readiness cannot authorize model work")

    gaps = readiness.get("gap_codes")
    if gaps != [CERTIFICATE_ONLY_GAP]:
        failures.append(
            "the only remaining readiness gap must be CORPUS_CERTIFICATE_NOT_CERTIFIED"
        )

    identity = readiness.get("evidence_identity_sha256")
    if not _is_sha256(identity):
        failures.append("readiness evidence_identity_sha256 is missing or malformed")

    material = readiness.get("evidence_identity_material")
    if not isinstance(material, Mapping):
        failures.append("readiness evidence_identity_material is missing")
    else:
        if not _is_sha256(material.get("canonical_ledger_semantic_sha256")):
            failures.append("readiness semantic ledger identity is missing or malformed")
        if not _is_sha256(material.get("coverage_policy_sha256")):
            failures.append("readiness coverage policy identity is missing or malformed")
        closure_hashes = material.get("closure_evidence_sha256")
        if not isinstance(closure_hashes, Mapping) or not closure_hashes:
            failures.append("readiness semantic closure identity is missing")
        elif any(not _is_sha256(value) for value in closure_hashes.values()):
            failures.append("readiness semantic closure identity contains malformed hashes")

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
        closure_material = (
            material.get("closure_evidence_sha256")
            if isinstance(material, Mapping)
            else None
        )
        for node, row in sorted(nodes.items()):
            if not isinstance(row, Mapping):
                failures.append(f"closure evidence node {node} is malformed")
                continue
            if row.get("present") is not True or row.get("pass") is not True:
                failures.append(f"closure evidence node {node} is not PASS")
            digest = row.get("sha256")
            if not _is_sha256(digest):
                failures.append(f"closure evidence node {node} lacks a sha256")
            if isinstance(closure_material, Mapping) and closure_material.get(node) != digest:
                failures.append(f"closure evidence node {node} is not bound by semantic identity")

    inputs = readiness.get("inputs")
    if not isinstance(inputs, Mapping):
        failures.append("readiness inputs are missing")
    else:
        ledger = inputs.get("canonical_ledger_summary")
        policy = inputs.get("coverage_policy")
        if not isinstance(ledger, Mapping):
            failures.append("canonical ledger readiness input is missing")
        else:
            if not _is_sha256(ledger.get("sha256")):
                failures.append("canonical ledger summary provenance hash is malformed")
            if not _is_sha256(ledger.get("ledger_sha256")):
                failures.append("canonical semantic ledger hash is malformed")
            if not _is_commit_sha(ledger.get("baseline_commit")):
                failures.append("canonical ledger execution baseline is malformed")
            if isinstance(material, Mapping) and ledger.get("ledger_sha256") != material.get(
                "canonical_ledger_semantic_sha256"
            ):
                failures.append("canonical ledger input disagrees with semantic identity")
        if not isinstance(policy, Mapping) or not _is_sha256(policy.get("sha256")):
            failures.append("coverage policy readiness input lacks a sha256")
        elif isinstance(material, Mapping) and policy.get("sha256") != material.get(
            "coverage_policy_sha256"
        ):
            failures.append("coverage policy input disagrees with semantic identity")

    return failures


def build_corpus_certificate(
    *,
    readiness: Mapping[str, Any],
    git_commit: str,
    generated_at_utc: str,
    free_tier_policy_sha256: str,
    toolchain_certificate_sha256: str,
    documentation_certificate_sha256: str,
    github_run_id: str | None = None,
) -> dict[str, Any]:
    failures = validate_pre_certificate_readiness(readiness)
    if failures:
        raise ValueError("; ".join(failures))
    if not _is_commit_sha(git_commit):
        raise ValueError("certificate execution commit is missing or malformed")
    for name, digest in (
        ("free-tier policy", free_tier_policy_sha256),
        ("toolchain certificate", toolchain_certificate_sha256),
        ("documentation certificate", documentation_certificate_sha256),
    ):
        if not _is_sha256(digest):
            raise ValueError(f"{name} sha256 is missing or malformed")

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

    empirical_outputs = {
        DATASET_EMPIRICAL_ID: {
            "status": "PASS",
            "basis": [
                "canonical_ledger_summary",
                "coverage_gate",
                "freeze_1_validation",
                "freeze_2_validation",
                "reproducibility",
            ],
            "claim": (
                "Exact admitted real corpus identity, counts, durations, recording groups "
                "and deterministic splits are frozen and reproducible for this semantic evidence identity."
            ),
        },
        DATA_QUALITY_EMPIRICAL_ID: {
            "status": "PASS",
            "basis": [
                "global_dedup_audit",
                "recording_family_audit",
                "split_integrity",
                "coverage_gate",
            ],
            "claim": (
                "Rights/quality, duplicate, recording-family, split, coverage and source-diversity "
                "closure passed for this semantic evidence identity."
            ),
        },
    }

    payload: dict[str, Any] = {
        "schema_version": CERTIFICATE_SCHEMA_VERSION,
        "artifact_id": CORPUS_CERTIFICATE_ID,
        "artifact_version": CORPUS_CERTIFICATE_VERSION,
        "status": "CERTIFIED",
        "scope": "MK1 release_safe frozen acoustic corpus",
        "semantic_evidence_identity_sha256": readiness["evidence_identity_sha256"],
        "semantic_evidence_identity_material": dict(readiness["evidence_identity_material"]),
        "documentation": {
            "certificate": DOCUMENTATION_CERTIFICATE_ID,
            "path": DOCUMENTATION_CERTIFICATE_PATH,
            "sha256": documentation_certificate_sha256,
            "status": "CERTIFIED",
        },
        "free_tier_boundary": {
            "policy_id": FREE_TIER_POLICY_ID,
            "path": FREE_TIER_POLICY_PATH,
            "policy_sha256": free_tier_policy_sha256,
            "result": "PASS",
        },
        "inputs": {
            "toolchain_certificate": {
                "id": TOOLCHAIN_CERTIFICATE_ID,
                "path": TOOLCHAIN_CERTIFICATE_PATH,
                "sha256": toolchain_certificate_sha256,
                "status": "CERTIFIED",
            },
            "corpus_readiness": {
                "id": READINESS_ID,
                "schema_version": readiness["schema_version"],
                "evidence_identity_sha256": readiness["evidence_identity_sha256"],
                "eligible_for_certificate_review": True,
            },
            "canonical_ledger_summary": dict(readiness["inputs"]["canonical_ledger_summary"]),
            "coverage_policy": dict(readiness["inputs"]["coverage_policy"]),
        },
        "empirical_outputs": empirical_outputs,
        "outputs": [{"path": CERTIFICATE_PATH}],
        "criteria": [
            {"id": "CORPUS_READINESS_ELIGIBLE", "result": "PASS"},
            {"id": DATASET_EMPIRICAL_ID, "result": "PASS"},
            {"id": DATA_QUALITY_EMPIRICAL_ID, "result": "PASS"},
            {"id": "ALL_CLOSURE_EVIDENCE_PASS", "result": "PASS"},
            {"id": "ONLY_CERTIFICATE_GAP_REMAINED", "result": "PASS"},
            {"id": TOOLCHAIN_CERTIFICATE_ID, "result": "PASS"},
            {"id": DOCUMENTATION_CERTIFICATE_ID, "result": "PASS"},
            {"id": FREE_TIER_POLICY_ID, "result": "PASS"},
        ],
        "issuance_provenance": {
            "execution_commit": git_commit,
            "generated_at_utc": generated_at_utc,
            "github_run_id": github_run_id,
            "note": (
                "Issuance provenance is auditable. Certificate validity is additionally bound to "
                "semantic evidence identity and current certified ancestor hashes."
            ),
        },
        "evidence": evidence,
        "non_claims": [
            "Does not certify a model winner, model metrics, thresholds, field performance, distance/SNR envelope or real-camera operation.",
            "Does not broaden release_safe licensing beyond the exact corpus identity and rights evidence bound by the certificate.",
        ],
        "invalidates_if": [
            "semantic corpus/readiness evidence identity changes",
            "coverage policy changes",
            "any dedup, recording-family, split, coverage, freeze or reproducibility evidence changes",
            "source, asset, rights, mapping, grouping, fingerprint or freeze semantics change",
            "CERT-MK1-DF-TOOLCHAIN-005 changes or invalidates",
            "CERT-DOC-015 changes or invalidates",
            "ECHO-FREE-TIER-001 policy changes or is violated",
        ],
        "hash_contract": (
            "certificate_sha256 is SHA-256 over canonical JSON of this object with "
            "certificate_sha256 omitted"
        ),
    }
    payload["certificate_sha256"] = certificate_sha256(payload)
    return payload


def validate_corpus_certificate(
    certificate: Mapping[str, Any],
    *,
    evidence_identity_sha256: str,
    free_tier_policy_sha256: str | None = None,
    toolchain_certificate_sha256: str | None = None,
    documentation_certificate_sha256: str | None = None,
) -> list[str]:
    failures: list[str] = []

    if certificate.get("schema_version") != CERTIFICATE_SCHEMA_VERSION:
        failures.append("unexpected certificate schema_version")
    if certificate.get("artifact_id") != CORPUS_CERTIFICATE_ID:
        failures.append("unexpected certificate artifact_id")
    if str(certificate.get("status") or "").upper() != "CERTIFIED":
        failures.append("certificate status is not CERTIFIED")
    if certificate.get("semantic_evidence_identity_sha256") != evidence_identity_sha256:
        failures.append("certificate semantic evidence identity does not match readiness")

    boundary = certificate.get("free_tier_boundary")
    if not isinstance(boundary, Mapping):
        failures.append("free_tier_boundary is missing")
    else:
        if boundary.get("policy_id") != FREE_TIER_POLICY_ID:
            failures.append("unexpected free-tier policy id")
        if str(boundary.get("result") or "").upper() != "PASS":
            failures.append("free-tier boundary did not PASS")
        if not _is_sha256(boundary.get("policy_sha256")):
            failures.append("free-tier policy sha256 is missing or malformed")
        if free_tier_policy_sha256 is not None and boundary.get("policy_sha256") != free_tier_policy_sha256:
            failures.append("free-tier policy ancestor hash drifted")

    inputs = certificate.get("inputs")
    readiness_input = inputs.get("corpus_readiness") if isinstance(inputs, Mapping) else None
    if not isinstance(readiness_input, Mapping):
        failures.append("certificate readiness input is missing")
    elif readiness_input.get("evidence_identity_sha256") != evidence_identity_sha256:
        failures.append("certificate readiness input does not match semantic evidence identity")

    toolchain = inputs.get("toolchain_certificate") if isinstance(inputs, Mapping) else None
    if not isinstance(toolchain, Mapping) or toolchain.get("id") != TOOLCHAIN_CERTIFICATE_ID:
        failures.append("required toolchain certificate ancestor is missing")
    else:
        if str(toolchain.get("status") or "").upper() != "CERTIFIED":
            failures.append("toolchain certificate ancestor is not certified")
        if not _is_sha256(toolchain.get("sha256")):
            failures.append("toolchain certificate ancestor hash is malformed")
        if toolchain_certificate_sha256 is not None and toolchain.get("sha256") != toolchain_certificate_sha256:
            failures.append("toolchain certificate ancestor hash drifted")

    documentation = certificate.get("documentation")
    if not isinstance(documentation, Mapping) or documentation.get("certificate") != DOCUMENTATION_CERTIFICATE_ID:
        failures.append("required documentation certificate ancestor is missing")
    else:
        if str(documentation.get("status") or "").upper() != "CERTIFIED":
            failures.append("documentation certificate ancestor is not certified")
        if not _is_sha256(documentation.get("sha256")):
            failures.append("documentation certificate ancestor hash is malformed")
        if documentation_certificate_sha256 is not None and documentation.get("sha256") != documentation_certificate_sha256:
            failures.append("documentation certificate ancestor hash drifted")

    empirical = certificate.get("empirical_outputs")
    if not isinstance(empirical, Mapping):
        failures.append("empirical_outputs are missing")
    else:
        for node in (DATASET_EMPIRICAL_ID, DATA_QUALITY_EMPIRICAL_ID):
            row = empirical.get(node)
            if not isinstance(row, Mapping) or str(row.get("status") or "").upper() != "PASS":
                failures.append(f"{node} is not PASS")

    criteria = certificate.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        failures.append("certificate criteria are missing")
    elif any(
        not isinstance(row, Mapping)
        or str(row.get("result") or "").upper() != "PASS"
        for row in criteria
    ):
        failures.append("certificate contains a non-PASS criterion")

    claimed_hash = certificate.get("certificate_sha256")
    if not _is_sha256(claimed_hash):
        failures.append("certificate_sha256 is missing or malformed")
    elif claimed_hash != certificate_sha256(certificate):
        failures.append("certificate_sha256 does not match certificate payload")

    return failures


def apply_corpus_certificate(
    readiness: dict[str, Any],
    certificate: Mapping[str, Any],
    *,
    free_tier_policy_sha256: str | None = None,
    toolchain_certificate_sha256: str | None = None,
    documentation_certificate_sha256: str | None = None,
) -> dict[str, Any]:
    result = dict(readiness)
    failures = validate_corpus_certificate(
        certificate,
        evidence_identity_sha256=str(readiness.get("evidence_identity_sha256") or ""),
        free_tier_policy_sha256=free_tier_policy_sha256,
        toolchain_certificate_sha256=toolchain_certificate_sha256,
        documentation_certificate_sha256=documentation_certificate_sha256,
    )

    if failures:
        gaps = [
            gap
            for gap in list(result.get("gap_codes") or [])
            if gap != CERTIFICATE_ONLY_GAP
        ]
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
        "evidence_identity_sha256": certificate["semantic_evidence_identity_sha256"],
    }
    result["modeling_allowed"] = bool(
        result.get("eligible_for_certificate_review") and not result["gap_codes"]
    )
    result["status"] = "READY" if result["modeling_allowed"] else "BLOCKED"
    result["next_authorized_stage"] = (
        "BENCHMARK_A_B_C" if result["modeling_allowed"] else "CORPUS_FOUNDRY_CLOSURE"
    )
    return result
