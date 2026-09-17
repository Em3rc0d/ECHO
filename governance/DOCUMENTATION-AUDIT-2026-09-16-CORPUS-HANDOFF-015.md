# Documentation Audit — Corpus Certificate Handoff 015

**Certificate:** `CERT-DOC-015`  
**Status:** `CERTIFIED`  
**Date:** 2026-09-16  
**Scope:** atomic corpus evidence → corpus certificate → model-entry handoff  
**Global invariant:** `ECHO-FREE-TIER-001`

## Audited project promise

**Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

The handoff does not redefine this promise. Model, runtime, replay and camera work remain downstream of the acoustic corpus gate.

## Semantic corpus truth

The documentation audit preserves the current corpus facts exactly:

```text
semantic ledger sha256  cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1
readiness identity      4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
assets                  1141
fingerprints            1141 / 1141
ledger blockers         0
global dedup            PASS
recording family        PASS
split integrity         PASS
split quarantine        0
coverage gaps           16
CERT-MK1-DF-CORPUS-001  OPEN
modeling_allowed = false
Benchmark A/B/C         LOCKED
```

`baseline_commit` and the byte hash of the ledger summary are execution provenance. They are audited but are not semantic corpus identity.

## Current empirical gaps

The exact gap structure is unchanged: seven FIRE_ALARM positive/split gaps, one GLASS_SHATTER source-concentration gap and eight TIRE_SQUEAL positive/split gaps. The lower bounds remain FIRE +31 assets/+9 groups, TIRE +36 assets/+15 groups, and GLASS +47 surviving non-Freesound assets if the Freesound numerator remains 280.

No floor, split assignment, source-family identity, label or license was weakened to close these gaps.

## Toolchain authority

`CERT-MK1-DF-TOOLCHAIN-005` is now `CERTIFIED` for the proven closure-era implementation through atomic evidence + semantic readiness v2. Its real execution evidence is workflow run `35159518112` and durable commit `40b1fb44921dfa98cf4fba03e652c1b0fa5abd2f`.

## Stable handoff authority

`CERT-MK1-DF-HANDOFF-001` is the stable certificate-transition contract. It deliberately replaces any dependency on a rolling documentation-current certificate.

The authorized transition is:

```text
ledger + closure + freeze + reproducibility
→ pre-certificate readiness
→ exactly [CORPUS_CERTIFICATE_NOT_CERTIFIED]
→ CERT-MK1-DF-CORPUS-001
→ final readiness READY / gap_codes=[] / modeling_allowed=true
→ Benchmark A/B/C
```

If any other gap exists, certificate issuance is a no-op and model entry remains blocked.

## Atomic writer rule

There is exactly one durable corpus writer. The canonical orchestrator owns ledger, closure, readiness and conditional certificate issuance in the same exact-baseline run. Diagnostics and model-entry workflows remain read-only.

An existing invalid/stale corpus certificate is never silently overwritten. The emitter refuses historical overwrite so a materially different corpus requires explicit certification governance.

## Invalidation

DOC-015 becomes stale when semantic corpus facts, coverage/freeze/reproducibility semantics, Toolchain-005, the handoff contract, model-entry wiring, certificate status, immutable promise or `ECHO-FREE-TIER-001` materially changes. Execution-provenance-only churn does not by itself constitute semantic corpus drift.
