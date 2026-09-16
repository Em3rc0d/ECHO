# MK1 Data Foundry Toolchain Recertification 005

**Certificate:** `CERT-MK1-DF-TOOLCHAIN-005`  
**Status:** `CERTIFIED`  
**Date:** 2026-09-16  
**Scope:** closure-era Data Foundry implementation, deterministic corpus cascade, semantic readiness v2 and certificate handoff wiring  
**Global invariant:** `ECHO-FREE-TIER-001`

## Certified claim

The MK1 Data Foundry toolchain is certified for deterministic release-safe corpus construction and fail-closed transition control. This certificate is about the implementation/toolchain, not about current corpus sufficiency.

## Evidence

The closure-era implementation was hardened through the following sequence:

```text
PR #43  closure audits aligned to screen -> confirm -> group semantics
PR #47  exact-SHA pipeline hardening
PR #48  atomic corpus evidence cascade + readiness v2
```

Real post-merge execution evidence:

```text
implementation merge             7cabdceecec9389153af4335e5e3b4564259776b
atomic workflow run              35159518112
atomic durable evidence commit   40b1fb44921dfa98cf4fba03e652c1b0fa5abd2f
```

The real workflow run successfully completed:

- exact durable baseline resolution;
- global zero-cost enforcement;
- static corpus-pipeline wiring audit;
- canonical ledger build;
- closure evidence + readiness from the same ledger;
- full process-level deterministic repeat;
- byte comparison of durable outputs;
- JSON/compactness validation;
- main-movement guard;
- one atomic evidence commit.

## Certified invariants

The toolchain enforces:

```text
one durable corpus writer
screen -> confirm -> group near-duplicate semantics
no automatic near-duplicate merge
whole-group split protection
no manual split shopping
release-safe rights boundary
canonical fingerprints before closure
coverage floors cannot be lowered by the pipeline
ECHO-FREE-TIER-001 / 0 USD
readiness identity separates semantic content from execution provenance
model-entry remains locked without a valid corpus certificate
```

## Certificate handoff extension

`CERT-MK1-DF-HANDOFF-001` defines the stable issuance contract. The same atomic orchestrator owns certificate issuance so the pipeline never depends on recursive `GITHUB_TOKEN` push triggers.

A blocked corpus must produce no corpus certificate. A fully closed pre-certificate readiness state must contain exactly one gap, `CORPUS_CERTIFICATE_NOT_CERTIFIED`, before issuance is legal.

## Non-claims

This certificate does **not** claim:

- current coverage is sufficient;
- `CERT-MK1-DF-CORPUS-001` is certified;
- Benchmark A/B/C has run;
- a model winner exists;
- thresholds, replay or field/camera validation are complete.

Current empirical corpus gaps remain authoritative until real acquisition closes them.

## Invalidation

Recertification is required after material changes to admission/rights, fingerprints, grouping/dedup, split, coverage/freeze/reproducibility semantics, semantic readiness identity, certificate handoff semantics, model-entry guard wiring or the global free-tier boundary.
