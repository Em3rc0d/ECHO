#!/usr/bin/env python3
"""Fail-closed static audit for the MK1 corpus release pipeline wiring.

Durable corpus evidence is produced by one atomic orchestrator. This is deliberate:
commits pushed by the repository GITHUB_TOKEN do not recursively trigger ordinary
push workflows, so ledger -> closure -> readiness must not depend on bot-push
recursion. Source materializers hand off through workflow_run; the orchestrator
resolves the current durable main commit once, builds ledger + closure + readiness
from that exact baseline, verifies determinism, refuses persistence if main moved,
and commits the complete evidence cascade atomically.

The standalone closure/readiness workflows are diagnostics only and must remain
read-only. Model entry remains read-only and fail-closed on certified readiness.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

CANONICAL = WORKFLOWS / "mk1-canonical-ledger.yml"
CLOSURE = WORKFLOWS / "mk1-corpus-closure-evidence.yml"
READINESS = WORKFLOWS / "mk1-corpus-readiness.yml"
MODEL_ENTRY = WORKFLOWS / "mk1-model-entry-gate.yml"

EXACT_CHECKOUT = "ref: ${{ github.sha }}"
ATOMIC_CHECKOUT = "ref: ${{ github.event_name == 'workflow_run' && 'main' || github.sha }}"
PERSIST_TO_MAIN = "git push origin HEAD:main"

SOURCE_WORKFLOWS = (
    "MK1 Freesound Release Safe Materialization",
    "MK1 Freesound CC0 Free Materialization",
    "MK1 SONYC Free Materialization",
    "MK1 OpenGameArt Rubberduck CC0 Materialization",
    "MK1 OpenGameArt Glass Expansion Materialization",
    "MK1 Public Gap Materialization",
)

ATOMIC_BUILD_COMMANDS = (
    "python scripts/data_foundry/build_canonical_asset_ledger.py",
    "python scripts/data_foundry/resolve_global_recording_groups.py",
    "python scripts/data_foundry/build_corpus_closure_evidence.py",
    "python scripts/data_foundry/apply_split_conflict_quarantine.py",
    "python scripts/data_foundry/build_corpus_closure_readiness.py",
)

DURABLE_OUTPUTS = (
    "canonical-release-safe-asset-ledger.jsonl",
    "canonical-release-safe-asset-ledger-summary.json",
    "global-dedup-audit.json",
    "recording-family-audit.json",
    "split-integrity.json",
    "coverage-gate.json",
    "corpus-freeze-1.validation.json",
    "corpus-freeze-2.validation.json",
    "corpus-reproducibility.json",
    "corpus-closure-readiness.json",
)


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


def audit_atomic_orchestrator() -> None:
    label = CANONICAL.name
    text = read(CANONICAL)

    for needle in (
        "workflow_dispatch:",
        "workflow_run:",
        "push:",
        "branches: [main]",
        "contents: write",
        "cancel-in-progress: false",
        "group: mk1-corpus-evidence-pipeline-main",
        "github.event.workflow_run.conclusion == 'success'",
        "github.event.workflow_run.head_branch == 'main'",
        "github.ref == 'refs/heads/main'",
        ATOMIC_CHECKOUT,
        "fetch-depth: 1",
        "ECHO_PIPELINE_BASELINE=$(git rev-parse HEAD)",
        "python scripts/check_free_tier_boundary.py",
        "python scripts/check_corpus_pipeline_wiring.py",
        "git fetch origin main --depth=1",
        'test "$ECHO_PIPELINE_BASELINE" = "$(git rev-parse HEAD)"',
        'test "$ECHO_PIPELINE_BASELINE" = "$(git rev-parse origin/main)"',
        "evidence(mk1): refresh atomic corpus evidence cascade [skip ci]",
        PERSIST_TO_MAIN,
    ):
        require(text, needle, label)

    for workflow in SOURCE_WORKFLOWS:
        require(text, workflow, f"{label} source handoff")

    for command in ATOMIC_BUILD_COMMANDS:
        require(text, command, f"{label} atomic build")

    for output in DURABLE_OUTPUTS:
        require(text, output, f"{label} durable output")

    # Floating main is allowed only inside the workflow_run selector where the
    # exact resolved commit is captured immediately and guarded before persist.
    forbid(text, "ref: main\n", label)


def audit_diagnostic(path: Path, required_commands: tuple[str, ...]) -> None:
    label = path.name
    text = read(path)
    for needle in (
        "workflow_dispatch:",
        "contents: read",
        EXACT_CHECKOUT,
        "fetch-depth: 1",
        "python scripts/check_free_tier_boundary.py",
        "python scripts/check_corpus_pipeline_wiring.py",
    ):
        require(text, needle, label)
    for command in required_commands:
        require(text, command, label)

    for forbidden in (
        "workflow_run:",
        "push:\n",
        "contents: write",
        PERSIST_TO_MAIN,
        "git commit -m",
    ):
        forbid(text, forbidden, label)


def audit_model_entry() -> None:
    label = MODEL_ENTRY.name
    text = read(MODEL_ENTRY)
    for needle in (
        "workflow_dispatch:",
        "workflow_call:",
        "contents: read",
        EXACT_CHECKOUT,
        "fetch-depth: 1",
        "python scripts/check_free_tier_boundary.py",
        "build_corpus_closure_readiness.py --require-modeling-ready",
    ):
        require(text, needle, label)
    for forbidden in (
        "contents: write",
        PERSIST_TO_MAIN,
        "git commit -m",
    ):
        forbid(text, forbidden, label)


def main() -> int:
    audit_atomic_orchestrator()
    audit_diagnostic(
        CLOSURE,
        (
            "python scripts/data_foundry/build_corpus_closure_evidence.py",
            "python scripts/data_foundry/apply_split_conflict_quarantine.py",
        ),
    )
    audit_diagnostic(
        READINESS,
        ("python scripts/data_foundry/build_corpus_closure_readiness.py",),
    )
    audit_model_entry()

    print("MK1 corpus pipeline wiring PASS: atomic durable cascade + read-only diagnostics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
