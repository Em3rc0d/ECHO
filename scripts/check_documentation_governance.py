#!/usr/bin/env python3
"""Fail closed when ECHO documentation/certification truth drifts.

This checker intentionally validates only high-authority invariants that can be
checked deterministically in CI. It does not pretend to replace human review of
scientific evidence, licenses, semantics, or empirical claims.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

PROMISE = "Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial"
EXPECTED_MD_COUNT = 206

REQUIRED_FILES = {
    "charter": ROOT / "PROJECT-CHARTER.md",
    "state": ROOT / "CURRENT-STATE.md",
    "doc_standard": ROOT / "governance/DOCUMENTATION-STANDARD.md",
    "doc_coverage": ROOT / "governance/DOCUMENTATION-COVERAGE.md",
    "doc_audit": ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-13-CORPUS-CLOSURE.md",
    "cert_dag": ROOT / "governance/CERTIFICATION-DAG.md",
    "cert_ledger": ROOT / "governance/CERTIFICATION-LEDGER.md",
    "free_tier": ROOT / "governance/FREE-TIER-BOUNDARY.md",
    "closure_plan": ROOT / "MK1/build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md",
    "foundry_gates": ROOT / "MK1/build/data-foundry/FOUNDRY-GATES.md",
    "materialization": ROOT / "MK1/build/data-foundry/MATERIALIZATION.md",
    "toolchain_cert": ROOT / "MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-002.md",
}


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []

    for name, path in REQUIRED_FILES.items():
        require(path.is_file(), f"missing required documentation authority: {name} -> {path.relative_to(ROOT)}", failures)

    if failures:
        print("DOCUMENTATION GOVERNANCE: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    docs = {name: text(path) for name, path in REQUIRED_FILES.items()}

    # Immutable product promise must be visible in both scope authority and
    # current operational truth.
    require(PROMISE in docs["charter"], "immutable promise missing from PROJECT-CHARTER.md", failures)
    require(PROMISE in docs["state"], "immutable promise missing from CURRENT-STATE.md", failures)

    # Global governance authorities.
    require("FROZEN_DOCUMENTATION_GOVERNANCE" in docs["doc_standard"], "documentation standard is not frozen governance", failures)
    require("documentation-first" in docs["doc_standard"].casefold(), "documentation-first rule missing", failures)
    require("ECHO-FREE-TIER-001" in docs["doc_standard"], "documentation standard does not inherit free-tier boundary", failures)
    require("FROZEN_GLOBAL_POLICY" in docs["free_tier"], "free-tier policy is not marked FROZEN_GLOBAL_POLICY", failures)
    require("ECHO-FREE-TIER-001" in docs["free_tier"], "free-tier policy id missing", failures)
    require("0 USD" in docs["free_tier"], "zero-cost invariant missing from free-tier policy", failures)

    # Documentation certificate must be current and consistently represented.
    require("CERT-DOC-004" in docs["doc_coverage"] and "Current certificate" in docs["doc_coverage"], "DOCUMENTATION-COVERAGE does not name CERT-DOC-004 as current", failures)
    require(re.search(r"\|\s*CERT-DOC-004\s*\|.*\|\s*CERTIFIED\s*\|", docs["cert_ledger"]) is not None, "CERT-DOC-004 is not CERTIFIED in certification ledger", failures)
    require("CERT-DOC-004  CERTIFIED / current" in docs["state"], "CURRENT-STATE does not show CERT-DOC-004 as current certified documentation", failures)
    require("**Certificate:** `CERT-DOC-004`" in docs["doc_audit"], "current documentation audit does not bind CERT-DOC-004", failures)
    require("**Status:** `CERTIFIED`" in docs["doc_audit"], "current documentation audit is not CERTIFIED", failures)

    # Current Foundry engineering cert must be represented consistently.
    require(re.search(r"\|\s*CERT-MK1-DF-TOOLCHAIN-002\s*\|.*\|\s*CERTIFIED\s*\|", docs["cert_ledger"]) is not None, "current Foundry toolchain certificate missing/not certified in ledger", failures)
    require("CERT-MK1-DF-TOOLCHAIN-002  = CERTIFIED" in docs["state"], "CURRENT-STATE does not show toolchain-002 certified", failures)
    require("CERT-MK1-DF-TOOLCHAIN-002" in docs["foundry_gates"], "FOUNDRY-GATES does not point to current toolchain certificate", failures)

    # Empirical corpus must stay open until actual closure evidence exists.
    require(re.search(r"\|\s*CERT-MK1-DF-CORPUS-001\s*\|.*\|\s*OPEN\s*\|", docs["cert_ledger"]) is not None, "corpus certificate is not explicitly OPEN in ledger", failures)
    require("CERT-MK1-DF-CORPUS-001     = OPEN" in docs["state"], "CURRENT-STATE does not keep corpus certificate OPEN", failures)

    # Closure-critical nodes must remain visible until implemented/evidenced.
    closure_joined = docs["closure_plan"] + "\n" + docs["foundry_gates"] + "\n" + docs["state"]
    for marker in (
        "near-duplicate",
        "hard-negative",
        "recording-family",
        "second clean freeze",
        "gap_codes",
    ):
        require(marker.casefold() in closure_joined.casefold(), f"closure-critical marker missing: {marker}", failures)

    # Stale capacity guidance must not return as current execution instruction.
    materialization_cf = docs["materialization"].casefold()
    require("requires a persistent self-hosted" not in materialization_cf, "stale self-hosted materialization requirement reintroduced", failures)
    require("120 gib" not in materialization_cf, "stale 120 GiB materialization requirement reintroduced", failures)
    require("echo-free-tier-001" in materialization_cf, "materialization guide does not inherit free-tier boundary", failures)
    require("bounded shard" in materialization_cf or "bounded" in materialization_cf, "materialization guide lacks bounded execution model", failures)

    # Documentation certificate is content-corpus scoped. Any new Markdown must
    # force a reviewed certificate/count update rather than silently extending it.
    md_files = sorted(ROOT.rglob("*.md"))
    require(len(md_files) == EXPECTED_MD_COUNT, f"Markdown corpus drift: expected {EXPECTED_MD_COUNT}, found {len(md_files)}; documentation re-audit required", failures)

    # No unresolved merge conflict markers in authoritative Markdown.
    for path in md_files:
        body = text(path)
        if "<<<<<<< " in body or "=======\n" in body and ">>>>>>> " in body:
            failures.append(f"merge conflict marker found in {path.relative_to(ROOT)}")

    if failures:
        print("DOCUMENTATION GOVERNANCE: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    print("DOCUMENTATION GOVERNANCE: PASS")
    print("immutable promise: PASS")
    print("documentation certificate: CERT-DOC-004")
    print("foundry toolchain certificate: CERT-MK1-DF-TOOLCHAIN-002")
    print("corpus certificate: OPEN (correct until empirical closure)")
    print("markdown corpus files:", len(md_files))
    print("global boundary: ECHO-FREE-TIER-001")
    return 0


if __name__ == "__main__":
    sys.exit(main())
