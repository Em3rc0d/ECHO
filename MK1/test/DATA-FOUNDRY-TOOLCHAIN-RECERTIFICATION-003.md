# MK1 Data Foundry Toolchain Recertification 003

**Certificate:** `CERT-MK1-DF-TOOLCHAIN-003`  
**Status:** `CERTIFIED`  
**Certified code baseline:** `dc225803b5c066b365779fdc2b4b2f0984bb7e19`  
**Durable readiness evidence commit:** `aac662b770669bf633dd58a582514abcb39c30a1`  
**GitHub Actions run:** `34904125873`  
**Global invariant:** `ECHO-FREE-TIER-001`

## Purpose

This certificate supersedes `CERT-MK1-DF-TOOLCHAIN-002` after the Corpus Foundry toolchain gained a machine-readable closure-readiness evaluator and a fail-closed model-entry guard. It certifies the current executable engineering surface only; it does **not** certify a real corpus, a model, thresholds, replay, or a camera integration.

## Change under review

The recertified surface adds:

- deterministic `EMP-MK1-CORPUS-READINESS-001` generation;
- explicit `gap_codes` derived from the canonical ledger, coverage policy and closure evidence;
- distinction between `eligible_for_certificate_review` and `modeling_allowed`;
- `--require-modeling-ready`, which exits non-zero until the named corpus certificate is `CERTIFIED` and closure evidence is complete;
- reusable `MK1 Model Entry Gate` workflow;
- workflow-wiring guard that rejects future model/benchmark/train workflows that bypass the corpus gate;
- readiness JSON Schema and unit tests;
- a durable readiness workflow that rebuilds twice and compares output for deterministic identity.

## Evidence

GitHub Actions run `34904125873` executed `MK1 Data Foundry CI` on exact code baseline `dc225803b5c066b365779fdc2b4b2f0984bb7e19` and completed successfully for Python 3.10, 3.11 and 3.12. Every matrix job passed compilation, registries/policies/schemas, acquisition smoke tests, readiness generation, model-entry wiring validation, and the full Foundry unit/synthetic E2E suite.

Companion gates on the same baseline also passed:

- `ECHO Free-Tier Boundary` — run `34904125820` — PASS;
- `ECHO Documentation Governance` — run `34904125815` — PASS at the pre-recertification documentation baseline;
- `MK1 Corpus Closure Readiness` — run `34904125899` — PASS as an evidence-generation gate.

The readiness workflow then persisted `corpus-closure-readiness.json` in commit `aac662b770669bf633dd58a582514abcb39c30a1`. Its status is correctly `BLOCKED`, `modeling_allowed=false`, and `CERT-MK1-DF-CORPUS-001=OPEN` because empirical corpus closure has not passed.

## Fail-closed properties certified

The toolchain refuses to equate any of the following with corpus certification:

```text
source metadata
candidate counts
download success
canonical ledger construction
green unit tests
large positive pools for some classes
```

Model work is eligible only when the readiness artifact observes all required closure evidence as PASS, `gap_codes=[]`, and the governing corpus certificate itself is `CERTIFIED`.

A missing evidence file is an explicit gap, not an implicit skip. A missing fingerprint, insufficient target floor, insufficient underlying-source diversity, missing hard negatives, non-release-safe rights, or open certificate keeps model entry locked.

## What this certificate does not claim

`CERT-MK1-DF-TOOLCHAIN-003` does not claim:

- that FIRE_ALARM or TIRE_SQUEAL have enough admitted positives;
- that hard-negative floors are complete;
- that canonical fingerprint coverage is complete;
- that global near-duplicate/recording-family audits have passed;
- that split integrity or coverage has passed;
- that freeze #1/#2 are reproducible;
- that `EMP-DATASET-001`, `EMP-DATA-QUALITY-001`, or `CERT-MK1-DF-CORPUS-001` are closed.

Those remain empirical downstream nodes.

## Downstream consequence

The certified path is now:

```text
CERT-MK1-DF-TOOLCHAIN-003
        ↓
EMP-MK1-CORPUS-READINESS-001
        ↓
close every gap
        ↓
CERT-MK1-DF-CORPUS-001
        ↓
model-entry gate
        ↓
Benchmark A/B/C
```

Until the corpus certificate passes, the guard intentionally blocks YAMNet/PANNs/CNN training/benchmark execution.

## Invalidation

This certificate becomes stale if the readiness evaluator, its schema/tests, coverage policy semantics, ledger semantics, source-family semantics, model-entry guard, Foundry code/config/schema/test surface, or `ECHO-FREE-TIER-001` changes materially without rerunning the relevant CI and dependency review.
