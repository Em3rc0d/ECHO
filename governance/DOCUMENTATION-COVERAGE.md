# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-015`  
**Current Markdown corpus:** `221 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-16-CORPUS-HANDOFF-015.md`

## Rule

ECHO is documentation-first and evidence-first. Documentation preserves `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION`, and `TARGET`. Green CI never manufactures empirical corpus/model evidence. All current truth inherits `ECHO-FREE-TIER-001`.

## Certificate lineage

```text
CERT-DOC-001..014  historical / invalidated
CERT-DOC-015       current / 221 files / CERTIFIED
```

## Current audited truth

```text
CERT-DOC-015                    = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004       = INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005       = CERTIFIED
CERT-MK1-DF-SONYC-001           = CERTIFIED
CERT-MK1-DF-HANDOFF-001         = CERTIFIED
GLOBAL_DEDUP                     = PASS
RECORDING_FAMILY_AUDIT           = PASS
SPLIT_INTEGRITY                  = PASS
SPLIT_QUARANTINE_ASSETS          = 0
LEDGER_BLOCKERS                  = 0
EMP-MK1-CORPUS-READINESS-001    = BLOCKED
CERT-MK1-DF-CORPUS-001          = OPEN
modeling_allowed                 = false
Benchmark A/B/C                  = LOCKED
ECHO-FREE-TIER-001               = PASS
```

## Semantic identity and execution provenance

The canonical semantic ledger identity is:

```text
cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1
```

Closure/coverage binds material ledger identity:

```text
93be3dceee44df0dfc51ab38c078f1e1e6587ba91e4fbbc53c3b65065e58bfa8
```

Readiness v2 semantic evidence identity is:

```text
4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
```

`baseline_commit` and raw generated-summary SHA values remain execution provenance. They must be valid and auditable, but they do not redefine corpus identity when semantic ledger, policy and closure identities are unchanged.

## Atomic durable pipeline and certificate handoff

One authoritative writer owns corpus evidence and the conditional certificate transition:

```text
governed source evidence
→ canonical ledger
→ grouping
→ dedup / recording-family / split
→ coverage
→ freeze #1 / freeze #2 / reproducibility
→ pre-certificate readiness
→ conditional CERT-MK1-DF-CORPUS-001 emitter
→ final readiness
→ one atomic durable commit
```

The complete cascade is rebuilt twice and byte-compared for determinism. The exact baseline is checked against `origin/main` immediately before persistence. Standalone closure/readiness/model-entry diagnostics remain read-only.

`CERT-MK1-DF-HANDOFF-001` authorizes certificate issuance only when pre-certificate readiness has exactly:

```text
schema_version = echo.corpus-closure-readiness.v2
status = BLOCKED
eligible_for_certificate_review = true
modeling_allowed = false
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
gap_codes = [CORPUS_CERTIFICATE_NOT_CERTIFIED]
```

Any additional gap makes issuance a successful no-op. A valid certificate may unlock final readiness only for the exact matching semantic evidence identity and stable Toolchain-005 / Handoff-001 / Free-Tier ancestors.

## Structural closure

The near-duplicate contract remains `screen -> confirm -> group`, not `screen -> identity`:

```text
candidate threshold                      0.02
confirmed threshold                     0.002
max decoded-sample delta                 0.01
candidate relations                       855
candidate cross-group                     849
confirmed relations                         2
confirmed cross-group conflicts              0
length-rejected candidates                835
exact duplicate groups                      0
global acoustic components                  2
members reassigned                           4
```

Dedup, recording-family and split integrity are PASS. Original protected-split conflicts are 0; quarantined assets are 0; development assets are 1141. Review-only screening evidence remains durable but does not create transitive recording identity.

## Current final coverage

Coverage remains FAIL with exactly 16 empirical gaps.

```text
BACKGROUND 428 assets / 385 groups / 4 sources                     PASS

FIRE_ALARM
  19 assets / 16 groups / 3 sources / 460.864037 s
  BIGSOUNDBANK 4 / FREESOUND 12 / WIKIMEDIA_COMMONS 3
  train 17/14, validation 2/2, test 0/0
  HN 202 / 202 / 4                                                PASS

GLASS_SHATTER
  303 assets / 287 groups / 4 sources / 1244.131193 s
  BIGSOUNDBANK 16 / FREESOUND 280
  OPENGAMEART_RUBBERDUCK 6 / OPENGAMEART_TILL_BEHREND 1
  max single-source fraction 0.924092                              FAIL <= 0.80
  HN 440 / 410 / 2                                                PASS

SIREN 169 assets / 169 groups; HN 235 / 235 / 4                   PASS

TIRE_SQUEAL
  14 assets / 10 groups / 2 sources / 344.600098 s
  BIGSOUNDBANK 5 / FREESOUND 9
  train 11/8, validation 0/0, test 3/2
  HN 25 / 12 / 2                                                  PASS

VEHICLE_HORN 235 assets / 235 groups; HN 142 / 142 / 3            PASS
```

Asset-quality stop lines are all zero.

## Quantified remaining evidence

Current lower bounds remain FIRE +31 assets and +9 independent groups; TIRE +36 assets and +15 groups; GLASS requires at least +47 surviving non-Freesound positives if the Freesound numerator remains 280. These are lower bounds only. No manual split placement, source-family inflation, label coercion or floor weakening is authorized.

## Freeze/readiness state

```text
freeze #1       FAIL / UPSTREAM_COVERAGE_NOT_PASS only
freeze #2       FAIL / UPSTREAM_COVERAGE_NOT_PASS only
reproducibility FAIL / UPSTREAM_FREEZE_NOT_ELIGIBLE
readiness v2    BLOCKED
CERT-MK1-DF-CORPUS-001 OPEN
modeling_allowed=false
Benchmark A/B/C LOCKED
```

## Product direction

```text
release-safe corpus
→ corpus certificate
→ Benchmark A/B/C
→ model winner
→ Event Engine
→ Edge Agent
→ MQTT/replay
→ real camera
```

Supporting camera/UI/transport work must not redefine or preempt the acoustic detection/classification core.

## Automated governance

`scripts/check_documentation_governance.py` validates the immutable promise, Free Tier, DOC-015 lineage, TOOLCHAIN-005 and HANDOFF-001 authority, exact semantic corpus/readiness identities, structural PASS gates, zero split quarantine, exactly 16 coverage gaps, nine current readiness blockers, current FIRE/GLASS/TIRE/background truth, corpus certificate OPEN, `modeling_allowed=false`, the 221-file Markdown inventory and absence of merge-conflict markers.

## Invalidation

DOC-015 becomes stale when semantic corpus facts, coverage/freeze/reproducibility semantics, Toolchain-005, Handoff-001, certificate state, model-entry wiring, immutable promise or `ECHO-FREE-TIER-001` materially changes. Execution-provenance-only churn does not by itself constitute semantic corpus drift.