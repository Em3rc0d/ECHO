# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-014`  
**Current Markdown corpus:** `218 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-16-CORPUS-PIPELINE-014.md`

## Rule

ECHO is documentation-first and evidence-first. Documentation preserves `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION`, and `TARGET`. Green CI never manufactures empirical corpus/model evidence. All current truth inherits `ECHO-FREE-TIER-001`.

## Certificate lineage

```text
CERT-DOC-001..013  historical / invalidated
CERT-DOC-014       current / 218 files / CERTIFIED
```

## Current audited truth

```text
CERT-DOC-014                    = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004       = INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005       = CANDIDATE
CERT-MK1-DF-SONYC-001           = CERTIFIED
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

DOC-014 explicitly separates corpus identity from execution provenance.

The canonical semantic ledger identity is:

```text
cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1
```

Closure/coverage binds material ledger identity:

```text
93be3dceee44df0dfc51ab38c078f1e1e6587ba91e4fbbc53c3b65065e58bfa8
```

Readiness v2 projects semantic evidence identity:

```text
4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
```

`baseline_commit` and the raw summary-file SHA remain execution provenance. They must be valid and internally consistent but are not treated as corpus-content identity.

## Atomic durable pipeline

One authoritative writer now owns durable corpus evidence:

```text
governed materialization
→ canonical ledger
→ grouping
→ dedup / recording-family / split
→ coverage
→ freeze #1 / freeze #2 / reproducibility
→ readiness
→ one atomic evidence commit
```

The complete cascade is repeated and byte-compared for determinism before persistence. The resolved baseline is checked against `origin/main` immediately before the commit. Standalone closure/readiness workflows are read-only diagnostics.

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

Current lower bounds remain FIRE +31 assets and +9 independent groups; TIRE +36 assets and +15 groups; GLASS requires at least +47 surviving non-Freesound positives if the Freesound numerator remains 280. Split requirements are never filled by manual remapping: evidence enters the canonical pipeline and deterministic split assignment remains authoritative.

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

## Product-direction audit

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

## Acquisition boundary

New source lanes may materialize public rights/provenance/bytes/probe/fingerprint evidence before admission, but they receive zero corpus, split, coverage or diversity credit until source identity is reviewed, canonical-ledger integration is explicit, and the complete atomic grouping/dedup/split/coverage/readiness cascade succeeds.

Wrapper datasets/hosting sites never create independent acoustic-source credit by themselves.

## Automated governance

`scripts/check_documentation_governance.py` validates:

- immutable promise and `ECHO-FREE-TIER-001`;
- DOC-014 current / DOC-001..013 invalidated;
- SONYC-001 scoped certification;
- TOOLCHAIN-004 invalidated / TOOLCHAIN-005 candidate;
- canonical semantic ledger identity and 1141/1141 fingerprints;
- valid internally consistent execution provenance without treating it as data identity;
- readiness v2 semantic identity material;
- `screen -> confirm -> group` evidence counters and zero confirmed cross-family conflicts;
- dedup/family/split PASS and zero split quarantine;
- exactly 16 detailed coverage gaps and nine readiness blockers;
- current FIRE/GLASS/TIRE/background/hard-negative truth;
- final asset-quality stop lines all zero;
- corpus certificate OPEN and `modeling_allowed=false`;
- 218-file Markdown inventory and absence of merge-conflict markers.

## Invalidation

DOC-014 becomes stale if semantic corpus identity, durable closure/readiness evidence, certificate/policy truth, rights/semantics/grouping/split/coverage/freeze logic, immutable promise, product critical path or free-tier boundary changes without a fresh audit.

A pure execution provenance change does not redefine the corpus when all semantic evidence is identical, but provenance must still be valid and consistent.
