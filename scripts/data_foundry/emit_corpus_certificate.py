#!/usr/bin/env python3
"""Emit CERT-MK1-DF-CORPUS-001 only from a fully closed pre-certificate readiness state."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

from echo.data_foundry.certification import (
    CERTIFICATE_PATH,
    DOCUMENTATION_CERTIFICATE_ID,
    TOOLCHAIN_CERTIFICATE_ID,
    build_corpus_certificate,
    validate_corpus_certificate,
)
from echo.data_foundry.readiness import sha256_file

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_READINESS = ROOT / "MK1/mining-site/materialization/corpus-closure-readiness.json"
DEFAULT_OUTPUT = ROOT / CERTIFICATE_PATH
FREE_TIER_POLICY = ROOT / "configs/data_foundry/free_tier_boundary.v1.json"
TOOLCHAIN_CERTIFICATE = ROOT / "MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-004.md"
DOCUMENTATION_CERTIFICATE = ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-14-CORPUS-CERTIFICATION.md"


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def require_markdown_certificate(path: Path, certificate_id: str) -> str:
    if not path.is_file():
        raise SystemExit(f"required certified ancestor missing: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    if f"`{certificate_id}`" not in text and certificate_id not in text:
        raise SystemExit(f"{path.relative_to(ROOT)}: missing certificate id {certificate_id}")
    if "**Status:** `CERTIFIED`" not in text and "Status: CERTIFIED" not in text:
        raise SystemExit(f"{path.relative_to(ROOT)}: ancestor is not CERTIFIED")
    return sha256_file(path)


def existing_certificate_is_current(
    certificate: dict,
    *,
    evidence_identity_sha256: str,
    free_tier_sha256: str,
    toolchain_sha256: str,
    documentation_sha256: str,
) -> bool:
    if validate_corpus_certificate(
        certificate, evidence_identity_sha256=evidence_identity_sha256
    ):
        return False

    boundary = certificate.get("free_tier_boundary")
    if not isinstance(boundary, dict) or boundary.get("policy_sha256") != free_tier_sha256:
        return False

    inputs = certificate.get("inputs")
    if not isinstance(inputs, dict):
        return False
    toolchain = inputs.get("toolchain_certificate")
    if not isinstance(toolchain, dict) or toolchain.get("sha256") != toolchain_sha256:
        return False

    documentation = certificate.get("documentation")
    if not isinstance(documentation, list):
        return False
    doc_row = next(
        (
            row
            for row in documentation
            if isinstance(row, dict)
            and row.get("certificate") == DOCUMENTATION_CERTIFICATE_ID
        ),
        None,
    )
    return isinstance(doc_row, dict) and doc_row.get("sha256") == documentation_sha256


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readiness", type=Path, default=DEFAULT_READINESS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_free_tier_boundary.py")],
        cwd=ROOT,
        check=True,
    )

    free_tier_sha = sha256_file(FREE_TIER_POLICY)
    toolchain_sha = require_markdown_certificate(
        TOOLCHAIN_CERTIFICATE, TOOLCHAIN_CERTIFICATE_ID
    )
    documentation_sha = require_markdown_certificate(
        DOCUMENTATION_CERTIFICATE, DOCUMENTATION_CERTIFICATE_ID
    )

    readiness = json.loads(args.readiness.read_text(encoding="utf-8"))
    identity = str(readiness.get("evidence_identity_sha256") or "")

    if args.output.is_file():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if existing_certificate_is_current(
            existing,
            evidence_identity_sha256=identity,
            free_tier_sha256=free_tier_sha,
            toolchain_sha256=toolchain_sha,
            documentation_sha256=documentation_sha,
        ):
            print("CORPUS CERTIFICATE: CURRENT")
            print(existing["certificate_sha256"])
            return 0

    certificate = build_corpus_certificate(
        readiness=readiness,
        git_commit=git_head(),
        generated_at_utc=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        free_tier_policy_sha256=free_tier_sha,
        toolchain_certificate_sha256=toolchain_sha,
        documentation_certificate_sha256=documentation_sha,
        github_run_id=os.getenv("GITHUB_RUN_ID"),
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(certificate, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("CORPUS CERTIFICATE: CERTIFIED")
    print(certificate["certificate_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
