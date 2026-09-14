#!/usr/bin/env python3
"""Build or enforce the MK1 Corpus Foundry closure readiness gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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
DEFAULT_OUTPUT = MATERIALIZATION / "corpus-closure-readiness.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger-summary", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--coverage-policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--evidence-dir", type=Path, default=MATERIALIZATION)
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
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")

    if args.stdout:
        print(encoded, end="")
    else:
        print(result["readiness_id"], result["status"])
        print("eligible_for_certificate_review:", result["eligible_for_certificate_review"])
        print("modeling_allowed:", result["modeling_allowed"])
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
