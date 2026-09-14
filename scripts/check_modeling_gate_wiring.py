#!/usr/bin/env python3
"""Prevent model/benchmark workflows from bypassing the certified corpus gate."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github/workflows"

MODEL_MARKERS = ("benchmark", "model", "yamnet", "panns", "training", "train")
GUARD_MARKERS = (
    "build_corpus_closure_readiness.py --require-modeling-ready",
    "mk1-model-entry-gate.yml",
)


def main() -> int:
    failures: list[str] = []
    checked: list[str] = []

    for path in sorted(WORKFLOW_DIR.glob("*.yml")):
        name = path.name.casefold()
        body = path.read_text(encoding="utf-8")
        body_cf = body.casefold()
        is_modeling = any(marker in name for marker in MODEL_MARKERS)
        if not is_modeling:
            first_lines = "\n".join(body.splitlines()[:20]).casefold()
            is_modeling = any(marker in first_lines for marker in MODEL_MARKERS)
        if not is_modeling:
            continue

        checked.append(path.name)
        if path.name == "mk1-model-entry-gate.yml":
            if "--require-modeling-ready" not in body:
                failures.append(f"{path.name}: gate workflow does not enforce readiness")
            continue

        if not any(marker.casefold() in body_cf for marker in GUARD_MARKERS):
            failures.append(
                f"{path.name}: modeling workflow lacks CERT-MK1-DF-CORPUS-001 readiness guard"
            )

    if failures:
        print("MODEL WORKFLOW GATE WIRING: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    print("MODEL WORKFLOW GATE WIRING: PASS")
    print("modeling workflows checked:", len(checked))
    for name in checked:
        print(" -", name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
