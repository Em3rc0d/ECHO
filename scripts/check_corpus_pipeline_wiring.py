#!/usr/bin/env python3
"""Fail-closed static audit for the MK1 corpus release pipeline wiring.

The durable chain is intentionally push-driven:
source evidence -> canonical ledger -> closure evidence -> readiness -> model entry.
Each stage must check out the exact triggering commit and refuse persistence when
main moved underneath it.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

CANONICAL = WORKFLOWS / "mk1-canonical-ledger.yml"
CLOSURE = WORKFLOWS / "mk1-corpus-closure-evidence.yml"
READINESS = WORKFLOWS / "mk1-corpus-readiness.yml"
MODEL_ENTRY = WORKFLOWS / "mk1-model-entry-gate.yml"

EXACT_CHECKOUT = "ref: ${{ github.sha }}"
BASELINE_GUARD = 'test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"'
PERSIST_TO_MAIN = "git push origin HEAD:main"


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing workflow: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"{label}: missing required wiring: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise SystemExit(f"{label}: forbidden wiring present: {needle}")


def audit_persisting_stage(path: Path, required_inputs: tuple[str, ...]) -> str:
    label = path.name
    text = read(path)
    require(text, "workflow_dispatch:", label)
    require(text, "push:", label)
    require(text, "branches: [main]", label)
    require(text, EXACT_CHECKOUT, label)
    require(text, "fetch-depth: 1", label)
    require(text, "cancel-in-progress: false", label)
    require(text, "git fetch origin main --depth=1", label)
    require(text, BASELINE_GUARD, label)
    require(text, PERSIST_TO_MAIN, label)
    forbid(text, "workflow_run:", label)
    forbid(text, "ref: main", label)
    for item in required_inputs:
        require(text, item, label)
    return text


def main() -> int:
    canonical = audit_persisting_stage(
        CANONICAL,
        (
            "MK1/mining-site/materialization/freesound-release-safe-materialization.json",
            "MK1/mining-site/materialization/freesound-cc0-gap-assets-report.json",
            "MK1/mining-site/materialization/public-gap-assets-report.json",
        ),
    )
    closure = audit_persisting_stage(
        CLOSURE,
        (
            "MK1/mining-site/materialization/canonical-release-safe-asset-ledger.jsonl",
            "MK1/mining-site/materialization/canonical-release-safe-asset-ledger-summary.json",
        ),
    )
    readiness = audit_persisting_stage(
        READINESS,
        (
            "MK1/mining-site/materialization/global-dedup-audit.json",
            "MK1/mining-site/materialization/recording-family-audit.json",
            "MK1/mining-site/materialization/split-integrity.json",
            "MK1/mining-site/materialization/coverage-gate.json",
            "MK1/mining-site/materialization/corpus-freeze-1.validation.json",
            "MK1/mining-site/materialization/corpus-freeze-2.validation.json",
            "MK1/mining-site/materialization/corpus-reproducibility.json",
        ),
    )

    # Assert the handoff files that make the push-only chain self-propagating.
    for output in (
        "canonical-release-safe-asset-ledger.jsonl",
        "canonical-release-safe-asset-ledger-summary.json",
    ):
        require(closure, output, "canonical -> closure handoff")
    for output in (
        "global-dedup-audit.json",
        "recording-family-audit.json",
        "split-integrity.json",
        "coverage-gate.json",
        "corpus-freeze-1.validation.json",
        "corpus-freeze-2.validation.json",
        "corpus-reproducibility.json",
    ):
        require(readiness, output, "closure -> readiness handoff")

    # The producer stages must still be capable of durable persistence.
    require(canonical, "contents: write", CANONICAL.name)
    require(closure, "contents: write", CLOSURE.name)
    require(readiness, "contents: write", READINESS.name)

    model_entry = read(MODEL_ENTRY)
    require(model_entry, "workflow_call:", MODEL_ENTRY.name)
    require(model_entry, EXACT_CHECKOUT, MODEL_ENTRY.name)
    require(model_entry, "contents: read", MODEL_ENTRY.name)
    require(
        model_entry,
        "build_corpus_closure_readiness.py --require-modeling-ready",
        MODEL_ENTRY.name,
    )
    forbid(model_entry, "contents: write", MODEL_ENTRY.name)

    print("MK1 corpus pipeline wiring PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
