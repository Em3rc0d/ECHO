#!/usr/bin/env python3
"""Issue CERT-MK1-DF-CORPUS-001 only from exact closed pre-certificate readiness."""

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
    HANDOFF_CERTIFICATE_ID,
    HANDOFF_CERTIFICATE_PATH,
    TOOLCHAIN_CERTIFICATE_ID,
    TOOLCHAIN_CERTIFICATE_PATH,
    FREE_TIER_POLICY_PATH,
    build_corpus_certificate,
    validate_corpus_certificate,
    validate_pre_certificate_readiness,
)
from echo.data_foundry.readiness import load_json_object, sha256_file

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_READINESS = ROOT / "MK1/mining-site/materialization/corpus-closure-readiness.json"
DEFAULT_OUTPUT = ROOT / CERTIFICATE_PATH
FREE_TIER_POLICY = ROOT / FREE_TIER_POLICY_PATH
TOOLCHAIN_CERTIFICATE = ROOT / TOOLCHAIN_CERTIFICATE_PATH
HANDOFF_CERTIFICATE = ROOT / HANDOFF_CERTIFICATE_PATH


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def require_certified_markdown(path: Path, certificate_id: str) -> str:
    if not path.is_file():
        raise SystemExit(f"required certified authority missing: {path.relative_to(ROOT)}")
    body = path.read_text(encoding="utf-8")
    if certificate_id not in body:
        raise SystemExit(f"{path.relative_to(ROOT)}: missing authority id {certificate_id}")
    if "**Status:** `CERTIFIED`" not in body and "Status: CERTIFIED" not in body:
        raise SystemExit(f"{path.relative_to(ROOT)}: authority is not CERTIFIED")
    return sha256_file(path)


def ancestor_hashes() -> tuple[str, str, str]:
    if not FREE_TIER_POLICY.is_file():
        raise SystemExit(f"missing free-tier policy: {FREE_TIER_POLICY.relative_to(ROOT)}")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_free_tier_boundary.py")],
        cwd=ROOT,
        check=True,
    )
    return (
        sha256_file(FREE_TIER_POLICY),
        require_certified_markdown(TOOLCHAIN_CERTIFICATE, TOOLCHAIN_CERTIFICATE_ID),
        require_certified_markdown(HANDOFF_CERTIFICATE, HANDOFF_CERTIFICATE_ID),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readiness", type=Path, default=DEFAULT_READINESS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--if-eligible",
        action="store_true",
        help="Return success without emitting when corpus closure is not certificate-eligible.",
    )
    args = parser.parse_args()

    readiness = load_json_object(args.readiness)
    preflight_failures = validate_pre_certificate_readiness(readiness)
    if preflight_failures:
        print("CORPUS CERTIFICATE: BLOCKED")
        for failure in preflight_failures:
            print(" -", failure)
        return 0 if args.if_eligible else 3

    free_tier_sha, toolchain_sha, handoff_sha = ancestor_hashes()
    identity = str(readiness.get("evidence_identity_sha256") or "")

    if args.output.is_file():
        existing = load_json_object(args.output)
        failures = validate_corpus_certificate(
            existing,
            evidence_identity_sha256=identity,
            free_tier_policy_sha256=free_tier_sha,
            toolchain_certificate_sha256=toolchain_sha,
            handoff_certificate_sha256=handoff_sha,
        )
        if not failures:
            print("CORPUS CERTIFICATE: CURRENT")
            print(existing["certificate_sha256"])
            return 0
        print("CORPUS CERTIFICATE: REFUSE_OVERWRITE_INVALID_HISTORY")
        for failure in failures:
            print(" -", failure)
        return 4

    certificate = build_corpus_certificate(
        readiness=readiness,
        git_commit=git_head(),
        generated_at_utc=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        free_tier_policy_sha256=free_tier_sha,
        toolchain_certificate_sha256=toolchain_sha,
        handoff_certificate_sha256=handoff_sha,
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
