#!/usr/bin/env python3
"""Fail closed when ECHO documentation/certification truth drifts."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PROMISE = "Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial"
EXPECTED_MD_COUNT = 208

REQUIRED_FILES = {
    "charter": ROOT / "PROJECT-CHARTER.md",
    "state": ROOT / "CURRENT-STATE.md",
    "doc_standard": ROOT / "governance/DOCUMENTATION-STANDARD.md",
    "doc_coverage": ROOT / "governance/DOCUMENTATION-COVERAGE.md",
    "doc_audit": ROOT / "governance/DOCUMENTATION-AUDIT-2026-09-14-CORPUS-READINESS.md",
    "cert_dag": ROOT / "governance/CERTIFICATION-DAG.md",
    "cert_ledger": ROOT / "governance/CERTIFICATION-LEDGER.md",
    "free_tier": ROOT / "governance/FREE-TIER-BOUNDARY.md",
    "closure_plan": ROOT / "MK1/build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md",
    "foundry_gates": ROOT / "MK1/build/data-foundry/FOUNDRY-GATES.md",
    "materialization": ROOT / "MK1/build/data-foundry/MATERIALIZATION.md",
    "toolchain_cert": ROOT / "MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-003.md",
    "readiness": ROOT / "MK1/mining-site/materialization/corpus-closure-readiness.json",
}


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    for name, path in REQUIRED_FILES.items():
        require(path.is_file(), f"missing required authority: {name} -> {path.relative_to(ROOT)}", failures)
    if failures:
        print("DOCUMENTATION GOVERNANCE: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    docs = {name: text(path) for name, path in REQUIRED_FILES.items() if name != "readiness"}
    readiness = json.loads(REQUIRED_FILES["readiness"].read_text(encoding="utf-8"))

    require(PROMISE in docs["charter"], "immutable promise missing from charter", failures)
    require(PROMISE in docs["state"], "immutable promise missing from current state", failures)
    require("FROZEN_DOCUMENTATION_GOVERNANCE" in docs["doc_standard"], "documentation governance not frozen", failures)
    require("documentation-first" in docs["doc_standard"].casefold(), "documentation-first rule missing", failures)
    require("ECHO-FREE-TIER-001" in docs["doc_standard"], "documentation standard does not inherit free-tier boundary", failures)
    require("FROZEN_GLOBAL_POLICY" in docs["free_tier"], "free-tier policy not frozen", failures)
    require("0 USD" in docs["free_tier"], "zero-cost invariant missing", failures)

    require("CERT-DOC-005" in docs["doc_coverage"] and "Current certificate" in docs["doc_coverage"], "DOCUMENTATION-COVERAGE does not name CERT-DOC-005 as current", failures)
    require(re.search(r"\|\s*CERT-DOC-005\s*\|.*\|\s*CERTIFIED\s*\|", docs["cert_ledger"]) is not None, "CERT-DOC-005 not certified in ledger", failures)
    require("CERT-DOC-005                = CERTIFIED / current" in docs["state"], "CURRENT-STATE does not show CERT-DOC-005 current", failures)
    require("**Certificate:** `CERT-DOC-005`" in docs["doc_audit"], "current audit does not bind CERT-DOC-005", failures)
    require("**Status:** `CERTIFIED`" in docs["doc_audit"], "current documentation audit not certified", failures)

    require(re.search(r"\|\s*CERT-MK1-DF-TOOLCHAIN-003\s*\|.*\|\s*CERTIFIED\s*\|", docs["cert_ledger"]) is not None, "toolchain-003 missing/not certified", failures)
    require("CERT-MK1-DF-TOOLCHAIN-003  = CERTIFIED / current" in docs["state"], "CURRENT-STATE does not show toolchain-003 current", failures)
    require("CERT-MK1-DF-TOOLCHAIN-003" in docs["foundry_gates"], "FOUNDRY-GATES does not point to toolchain-003", failures)
    require("34904125873" in docs["toolchain_cert"], "toolchain-003 record missing CI run", failures)

    require(re.search(r"\|\s*CERT-MK1-DF-CORPUS-001\s*\|.*\|\s*OPEN\s*\|", docs["cert_ledger"]) is not None, "corpus certificate is not explicitly OPEN", failures)
    require("CERT-MK1-DF-CORPUS-001     = OPEN" in docs["state"], "CURRENT-STATE does not keep corpus certificate OPEN", failures)
    require(readiness.get("readiness_id") == "EMP-MK1-CORPUS-READINESS-001", "unexpected readiness id", failures)
    require(readiness.get("status") == "BLOCKED", "readiness must remain BLOCKED for current documented baseline", failures)
    require(readiness.get("modeling_allowed") is False, "modeling_allowed must be false while corpus OPEN", failures)
    require(readiness.get("corpus_certificate", {}).get("status") == "OPEN", "readiness corpus certificate status drift", failures)
    require(bool(readiness.get("gap_codes")), "current blocked readiness unexpectedly has no gap codes", failures)

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
    print("documentation certificate: CERT-DOC-005")
    print("foundry toolchain certificate: CERT-MK1-DF-TOOLCHAIN-003")
    print("corpus readiness: BLOCKED (correct current empirical state)")
    print("corpus certificate: OPEN")
    print("modeling_allowed: false")
    print("markdown corpus files:", len(md_files))
    print("global boundary: ECHO-FREE-TIER-001")
    return 0


if __name__ == "__main__":
    sys.exit(main())
