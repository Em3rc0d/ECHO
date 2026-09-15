#!/usr/bin/env python3
"""Build or enforce the MK1 Corpus Foundry closure readiness gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from echo.data_foundry.certification import (
    CERTIFICATE_PATH,
    DOCUMENTATION_CERTIFICATE_ID,
    TOOLCHAIN_CERTIFICATE_ID,
    apply_corpus_certificate,
)
from echo.data_foundry.readiness import (
    REQUIRED_EVIDENCE_NODES,
    evaluate_readiness,
    load_json_object,
    sha256_file,
)

ROOT = Path(__file__).resolve().parents[2]
MATERIALIZATION = ROOT / "MK1/mining-site/materialization"

DEFAULT_LEDGER = MATERIALIZATION / "canonical-release-safe-asset-ledger-summary.json"
DEFAULT_POLICY = ROOT / "configs/data_foundry/coverage_policy.v1.json"
DEFAULT_CERTIFICATE = ROOT / CERTIFICATE_PATH
DEFAULT_OUTPUT = MATERIALIZATION / "corpus-closure-readiness.json"
FREE_TIER_POLICY = ROOT / "configs/data_foundry/free_tier_boundary.v1.json"
TOOLCHAIN_CERTIFICATE = ROOT / "MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-004.md"
DOCUMENTATION_CERTIFICATE = ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-14-CORPUS-CERTIFICATION.md"


def current_ancestor_failures(certificate: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    inputs = certificate.get("inputs")
    inputs = inputs if isinstance(inputs, dict) else {}

    toolchain = inputs.get("toolchain_certificate")
    toolchain = toolchain if isinstance(toolchain, dict) else {}
    if toolchain.get("id") != TOOLCHAIN_CERTIFICATE_ID:
        failures.append("toolchain certificate id drifted")
    if not TOOLCHAIN_CERTIFICATE.is_file():
        failures.append("toolchain certificate ancestor is missing")
    elif toolchain.get("sha256") != sha256_file(TOOLCHAIN_CERTIFICATE):
        failures.append("toolchain certificate ancestor hash drifted")

    documentation = certificate.get("documentation")
    documentation = documentation if isinstance(documentation, list) else []
    doc_row = next(
        (
            row
            for row in documentation
            if isinstance(row, dict)
            and row.get("certificate") == DOCUMENTATION_CERTIFICATE_ID
        ),
        None,
    )
    if not DOCUMENTATION_CERTIFICATE.is_file():
        failures.append("documentation certificate ancestor is missing")
    elif not isinstance(doc_row, dict):
        failures.append("documentation certificate ancestor is not bound")
    elif doc_row.get("sha256") != sha256_file(DOCUMENTATION_CERTIFICATE):
        failures.append("documentation certificate ancestor hash drifted")

    boundary = certificate.get("free_tier_boundary")
    boundary = boundary if isinstance(boundary, dict) else {}
    if not FREE_TIER_POLICY.is_file():
        failures.append("free-tier policy is missing")
    elif boundary.get("policy_sha256") != sha256_file(FREE_TIER_POLICY):
        failures.append("free-tier policy hash drifted")

    return failures


def invalidate_for_ancestor_drift(
    result: dict[str, Any], failures: list[str]
) -> dict[str, Any]:
    gaps = list(result.get("gap_codes") or [])
    if "CORPUS_CERTIFICATE_INVALID" not in gaps:
        gaps.append("CORPUS_CERTIFICATE_INVALID")
    result["gap_codes"] = sorted(dict.fromkeys(gaps))
    result["corpus_certificate"] = {
        "id": "CERT-MK1-DF-CORPUS-001",
        "status": "INVALIDATED",
        "validation_failures": failures,
    }
    result["modeling_allowed"] = False
    result["status"] = "BLOCKED"
    result["next_authorized_stage"] = "CORPUS_FOUNDRY_CLOSURE"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger-summary", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--coverage-policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--evidence-dir", type=Path, default=MATERIALIZATION)
    parser.add_argument("--corpus-certificate", type=Path, default=DEFAULT_CERTIFICATE)
    parser.add_argument("--ignore-corpus-certificate", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-modeling-ready", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    ledger = load_json_object(args.ledger_summary)
    policy = load_json_object(args.coverage_policy)

    evidence = {}
    hashes: dict[str, str | None] = {
        "canonical_ledger_summary": sha256_file(args.ledger_summary),
        "coverage_policy": sha256_file(args.coverage_policy),
    }
    for node, filename in REQUIRED_EVIDENCE_NODES.items():
        path = args.evidence_dir / filename
        if path.is_file():
            evidence[node] = load_json_object(path)
            hashes[node] = sha256_file(path)
        else:
            evidence[node] = None
            hashes[node] = None

    result = evaluate_readiness(
        ledger_summary=ledger,
        coverage_policy=policy,
        evidence_artifacts=evidence,
        evidence_hashes=hashes,
    )

    if not args.ignore_corpus_certificate and args.corpus_certificate.is_file():
        certificate = load_json_object(args.corpus_certificate)
        ancestor_failures = current_ancestor_failures(certificate)
        if ancestor_failures:
            result = invalidate_for_ancestor_drift(result, ancestor_failures)
        else:
            result = apply_corpus_certificate(result, certificate)
        result["corpus_certificate"]["path"] = str(
            args.corpus_certificate.resolve().relative_to(ROOT.resolve())
        )
        result["corpus_certificate"]["file_sha256"] = sha256_file(
            args.corpus_certificate
        )

    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")

    if args.stdout:
        print(encoded, end="")
    else:
        print(result["readiness_id"], result["status"])
        print("eligible_for_certificate_review:", result["eligible_for_certificate_review"])
        print("modeling_allowed:", result["modeling_allowed"])
        print("certificate_status:", result["corpus_certificate"]["status"])
        print("gap_codes:", len(result["gap_codes"]))
        for gap in result["gap_codes"]:
            print(" -", gap)

    if args.require_modeling_ready and not result["modeling_allowed"]:
        print("MODEL ENTRY GATE: BLOCKED")
        return 3
    if args.require_modeling_ready:
        print("MODEL ENTRY GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
