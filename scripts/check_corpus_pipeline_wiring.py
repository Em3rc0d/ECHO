#!/usr/bin/env python3
"""Fail-closed static audit for the MK1 corpus release pipeline wiring.

Durable corpus evidence and certificate issuance are owned by one atomic orchestrator.
This avoids recursive GITHUB_TOKEN trigger assumptions and prevents a split-brain
ledger -> closure -> readiness -> certificate transition. Standalone closure/readiness
workflows remain read-only diagnostics. Model entry remains read-only and requires
certified readiness. Acquisition workflows that feed the orchestrator must also stay
bound to the exact configuration files that govern their candidate set.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

CANONICAL = WORKFLOWS / "mk1-canonical-ledger.yml"
CLOSURE = WORKFLOWS / "mk1-corpus-closure-evidence.yml"
READINESS = WORKFLOWS / "mk1-corpus-readiness.yml"
MODEL_ENTRY = WORKFLOWS / "mk1-model-entry-gate.yml"
FREESOUND_CC0 = WORKFLOWS / "mk1-freesound-cc0-free-materialization.yml"
HANDOFF = ROOT / "MK1/build/data-foundry/CORPUS-CERTIFICATE-HANDOFF.md"
TOOLCHAIN = ROOT / "MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-005.md"
CERTIFICATION = ROOT / "src/echo/data_foundry/certification.py"
EMITTER = ROOT / "scripts/data_foundry/emit_corpus_certificate.py"
CERT_SCHEMA = ROOT / "schemas/data_foundry/corpus-certificate.schema.json"

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
    "MK1 SoundBible Mike Koenig Tire Materialization",
)

ATOMIC_BUILD_COMMANDS = (
    "python scripts/data_foundry/build_canonical_asset_ledger.py",
    "python scripts/data_foundry/augment_canonical_ledger_with_soundbible_tire.py",
    "python scripts/data_foundry/resolve_global_recording_groups.py",
    "python scripts/data_foundry/balance_release_safe_corpus_sources.py",
    "python scripts/data_foundry/build_corpus_closure_evidence.py",
    "python scripts/data_foundry/apply_split_conflict_quarantine.py",
    "build_corpus_closure_readiness.py --ignore-corpus-certificate",
    "emit_corpus_certificate.py --readiness /tmp/corpus-readiness.pre-cert.json --if-eligible",
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
    "cert-mk1-df-corpus-001.json",
)


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing authority/workflow: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"{label}: missing required wiring: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise SystemExit(f"{label}: forbidden wiring present: {needle}")


def audit_certificate_authorities() -> None:
    handoff = read(HANDOFF)
    toolchain = read(TOOLCHAIN)
    certification = read(CERTIFICATION)
    emitter = read(EMITTER)
    schema = read(CERT_SCHEMA)

    for needle in (
        "CERT-MK1-DF-HANDOFF-001",
        "**Status:** `CERTIFIED`",
        "gap_codes = [CORPUS_CERTIFICATE_NOT_CERTIFIED]",
        "canonical corpus orchestrator is the only durable writer",
        "rolling documentation-current certificate is deliberately not a runtime ancestor",
    ):
        require(handoff, needle, HANDOFF.name)

    for needle in (
        "CERT-MK1-DF-TOOLCHAIN-005",
        "**Status:** `CERTIFIED`",
        "35159518112",
        "40b1fb44921dfa98cf4fba03e652c1b0fa5abd2f",
    ):
        require(toolchain, needle, TOOLCHAIN.name)

    for needle in (
        'CERTIFICATE_SCHEMA_VERSION = "echo.corpus-certificate.v2"',
        'TOOLCHAIN_CERTIFICATE_ID = "CERT-MK1-DF-TOOLCHAIN-005"',
        'HANDOFF_CERTIFICATE_ID = "CERT-MK1-DF-HANDOFF-001"',
        "validate_pre_certificate_readiness",
        "validate_corpus_certificate",
        "apply_corpus_certificate",
    ):
        require(certification, needle, CERTIFICATION.name)
    require(emitter, "REFUSE_OVERWRITE_INVALID_HISTORY", EMITTER.name)
    require(emitter, "--if-eligible", EMITTER.name)

    for needle in (
        '"schema_version": {"const": "echo.corpus-certificate.v2"}',
        '"artifact_id": {"const": "CERT-MK1-DF-CORPUS-001"}',
        '"certificate": {"const": "CERT-MK1-DF-HANDOFF-001"}',
        '"id": {"const": "CERT-MK1-DF-TOOLCHAIN-005"}',
    ):
        require(schema, needle, CERT_SCHEMA.name)


def audit_freesound_cc0_acquisition() -> None:
    label = FREESOUND_CC0.name
    text = read(FREESOUND_CC0)
    for needle in (
        "push:",
        "branches: [main]",
        "workflow_dispatch:",
        "contents: write",
        EXACT_CHECKOUT,
        "fetch-depth: 0",
        "configs/data_foundry/freesound_cc0_supplemental.v1.json",
        "MK1/mining-site/materialization/freesound-gap-discovery.json",
        "python scripts/materialize_freesound_cc0_gap_assets.py",
        "python scripts/data_foundry/enrich_freesound_cc0_fingerprints.py",
        "main moved during Freesound CC0 materialization; refusing to persist stale evidence",
        "evidence(mk1): materialize fingerprinted Freesound CC0 gap candidates",
        PERSIST_TO_MAIN,
    ):
        require(text, needle, label)
    forbid(text, "ref: main\n", label)


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
        "schemas/data_foundry/corpus-certificate.schema.json",
        "MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-005.md",
        "MK1/build/data-foundry/CORPUS-CERTIFICATE-HANDOFF.md",
        "cert-mk1-df-corpus-001.json",
        "assert final.get('modeling_allowed') is True",
        "assert final.get('modeling_allowed') is False",
        "cmp /tmp/echo-cascade-first/corpus-readiness.pre-cert.json /tmp/corpus-readiness.pre-cert.json",
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
        "emit_corpus_certificate.py",
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
        "emit_corpus_certificate.py",
    ):
        forbid(text, forbidden, label)


def main() -> int:
    audit_certificate_authorities()
    audit_freesound_cc0_acquisition()
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

    print("MK1 corpus pipeline wiring PASS: acquisition trigger + atomic evidence + certificate handoff + read-only model entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
