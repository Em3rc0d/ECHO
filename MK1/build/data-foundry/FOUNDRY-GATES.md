# MK1 Data Foundry — Gates and Closure Criteria

**Status:** `TOOLCHAIN_CERTIFIED / SONYC_CERTIFIED / CORPUS_CLOSURE_ACTIVE`  
**Toolchain:** `CERT-MK1-DF-TOOLCHAIN-005 = CERTIFIED`  
**SONYC:** `CERT-MK1-DF-SONYC-001 = CERTIFIED`  
**Handoff:** `CERT-MK1-DF-HANDOFF-001 = CERTIFIED`  
**Corpus:** `CERT-MK1-DF-CORPUS-001 = OPEN`  
**Readiness:** `EMP-MK1-CORPUS-READINESS-001 = BLOCKED`  
**Readiness identity:** `4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405`  
**Global invariant:** `ECHO-FREE-TIER-001`

## Gate chain

```text
DF-G0 source registry
→ DF-G1 provenance/acquisition
→ DF-G2 rights
→ DF-G3 exact semantics / governed hard negatives
→ DF-G4 real-byte integrity + probe + canonical fingerprint
→ corpus-role boundary
→ DF-G5 global dedup + acoustic recording-family closure
→ DF-G6 group-aware split / conflict quarantine
→ coverage/diversity/hard-negative solidity
→ DF-G7 freeze #1 → clean freeze #2 → reproducibility
→ pre-certificate readiness
→ CERT-MK1-DF-CORPUS-001
→ final readiness READY
→ DF-G8 model-entry → Benchmark A/B/C
```

No downstream gate compensates for an upstream failure. No paid fallback, label coercion, wrapper double-counting, source-family inflation, seed/split shopping or floor reduction is permitted.

## Certified Toolchain-005

`CERT-MK1-DF-TOOLCHAIN-005` is certified for the closure-era Foundry implementation through deterministic atomic corpus evidence and readiness v2.

```text
PR #43                          screen → confirm → group closure semantics
PR #47                          exact-SHA pipeline hardening
PR #48                          atomic corpus cascade + readiness v2
implementation merge            7cabdceecec9389153af4335e5e3b4564259776b
real atomic workflow run         35159518112
durable evidence commit          40b1fb44921dfa98cf4fba03e652c1b0fa5abd2f
```

This certification is implementation-scoped. It does not claim current corpus sufficiency.

## Structural gates — PASS

```text
corpus-facing assets                1141
canonical fingerprints              1141 / 1141
missing fingerprints                0
ledger blockers                     0
recording families                  1075
global dedup                        PASS
global recording-family audit       PASS
split integrity                     PASS
protected split conflicts           0
split quarantine                    0 assets
exact duplicate groups              0
confirmed near-duplicate cross-group conflicts 0
```

The near-duplicate contract is `screen -> confirm -> group`. Broad RMS-envelope proximity is screening only. Review-only edges never create transitive recording identity.

## Semantic identity boundary

```text
semantic ledger sha256   cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1
coverage ledger sha256   93be3dceee44df0dfc51ab38c078f1e1e6587ba91e4fbbc53c3b65065e58bfa8
readiness-v2 identity    4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
```

Execution commit and generated-summary byte hashes remain provenance, not corpus identity.

## Corpus solidity — frozen

`MK1-CORPUS-SOLIDITY-001` remains unchanged.

Per target:

```text
assets >= 50
groups >= 25
underlying sources >= 2
duration >= 180 s
largest source fraction <= 0.80
train >= 20 assets / 10 groups
validation >= 5 assets / 3 groups
test >= 5 assets / 3 groups
```

Per-target hard negatives require `>=20 assets / >=10 groups / >=2 underlying sources`. Global background/negatives require `>=200 assets / >=50 groups / >=3 sources`.

## Current empirical gaps

Coverage remains `FAIL` with exactly 16 empirical gaps.

```text
FIRE_ALARM
  assets 19/50
  groups 16/25
  lower bound +31 assets / +9 groups
  test 0/0; validation 2/2; train 17/14

GLASS_SHATTER
  assets 303 / groups 287 / sources 4
  Freesound 280 / total 303
  concentration 0.924092 > 0.80
  lower bound +47 surviving non-Freesound positives if Freesound remains 280

TIRE_SQUEAL
  assets 14/50
  groups 10/25
  lower bound +36 assets / +15 groups
  validation 0/0; test 3/2; train 11/8
```

BACKGROUND and current hard-negative floors are PASS. Asset-quality stop lines remain zero.

## DF-G7 — freeze and reproducibility

```text
freeze #1       FAIL / UPSTREAM_COVERAGE_NOT_PASS only
freeze #2       FAIL / UPSTREAM_COVERAGE_NOT_PASS only
reproducibility FAIL / UPSTREAM_FREEZE_NOT_ELIGIBLE
```

When coverage becomes PASS, the atomic orchestrator rebuilds freeze #1/#2 and reproducibility from the same exact baseline and verifies deterministic repeat before any durable commit.

## Corpus certificate handoff

`CERT-MK1-DF-HANDOFF-001` defines the only authorized transition. A certificate may be emitted only when freshly rebuilt pre-certificate readiness has:

```text
schema_version = echo.corpus-closure-readiness.v2
eligible_for_certificate_review = true
status = BLOCKED
modeling_allowed = false
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
gap_codes = [CORPUS_CERTIFICATE_NOT_CERTIFIED]
```

Every closure node must be PASS and bound by semantic readiness identity. Toolchain-005, Handoff-001 and `ECHO-FREE-TIER-001` are SHA-bound certificate ancestors. Any additional gap makes issuance a no-op.

## DF-G8 — model entry

After valid certificate application, and only then:

```text
status = READY
modeling_allowed = true
gap_codes = []
next_authorized_stage = BENCHMARK_A_B_C
```

Until that exact transition, no Benchmark A/B/C, YAMNet/PANNs/CNN training, threshold calibration, replay progression or real-camera progression is authorized.

## Active priority

Infrastructure polish is no longer the active objective after this handoff. The active blocker is empirical acquisition and admission:

```text
1. FIRE_ALARM genuine release-safe positives
2. TIRE_SQUEAL genuine release-safe positives
3. non-Freesound GLASS_SHATTER positives for source concentration
4. rerun the same canonical cascade after each governed admission batch
```

New evidence receives zero corpus credit until rights, semantics, probe, fingerprint, grouping, dedup and deterministic split gates pass.

## Certificate lineage

```text
CERT-MK1-DF-SPEC-001        CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004   INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005   CERTIFIED
CERT-MK1-DF-SONYC-001       CERTIFIED / scoped
CERT-MK1-DF-HANDOFF-001     CERTIFIED
EMP-DATASET-001              OPEN
EMP-DATA-QUALITY-001         OPEN
CERT-MK1-DF-CORPUS-001      OPEN
```

## Invalidation

Material changes to taxonomy, source/acquisition, rights/mapping/review, probing/fingerprints, grouping/dedup, split/coverage/freeze/reproducibility semantics, readiness identity, certificate handoff, model-entry wiring, SONYC evidence or `ECHO-FREE-TIER-001` require dependency review and selective recertification.