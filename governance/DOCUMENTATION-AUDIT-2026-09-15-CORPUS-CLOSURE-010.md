# Documentation Audit — MK1 Corpus Closure 010

**Certificate:** `CERT-DOC-010`  
**Status:** `CERTIFIED`  
**Audit date:** 2026-09-15  
**Durable readiness commit:** `60dfa361eb344172973a96949d38e137fbfaf822`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`

## Scope

This audit supersedes `CERT-DOC-009` and rebinds documentation governance to the current durable corpus-closure evidence after the Till Behrend GLASS admission and the resulting deterministic closure/readiness cascade.

It does **not** pre-certify the Wikimedia FIRE acquisition proposed in PR #33. Candidate configuration/workflow changes in that PR receive zero empirical corpus credit until they merge to `main`, materialize real bytes, pass rights/probe/fingerprint checks, rebuild the canonical ledger, survive grouping/dedup/quarantine and are observed by the final coverage gate.

## Immutable product promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

The critical path remains corpus → corpus certificate → Benchmark A/B/C → model winner → Event Engine → Edge Agent → MQTT/replay → real camera. Camera/UI/transport work cannot preempt the acoustic core.

## Durable evidence audited

At `main@60dfa361eb344172973a96949d38e137fbfaf822`:

```text
canonical ledger baseline              05433347ebc35e67ab9f3bbd78a9e3a64c0bb9aa
canonical ledger entries               1159
canonical fingerprints                 1159 / 1159
canonical fingerprint missing          0
ledger blockers                        0
ledger sha256                          d4c0e78ef9111ef2cf3f2a44a9aea9d1e009afb5424dc7c851cbc9883186d19a

global acoustic grouping               PASS
global dedup                           PASS
recording-family audit                 PASS
split integrity                        PASS
protected split-conflict groups        2
quarantined assets                     93

coverage                               FAIL / 17 detailed gaps
freeze #1                              FAIL / coverage-gated
freeze #2                              FAIL / freeze-1-gated
reproducibility                        FAIL / frozen-corpus-gated

CERT-MK1-DF-CORPUS-001                 OPEN
eligible_for_certificate_review        false
modeling_allowed                       false
Benchmark A/B/C                        LOCKED
```

Readiness evidence identity:

```text
7c3dd6d518d8bc088a419b39e4dfb4894482def44906ca4561a4cc84f631f389
```

## Current target truth

```text
FIRE_ALARM
  final assets                         9
  independent groups                   6
  hard negatives                       206 / 206 groups / 4 sources
  train                                7 / 4 groups
  validation                           2 / 2 groups
  test                                 0 / 0 groups

GLASS_SHATTER
  final assets                         239
  independent groups                   222
  BIGSOUNDBANK                         6
  FREESOUND                            226
  OPENGAMEART_RUBBERDUCK               6
  OPENGAMEART_TILL_BEHREND             1
  max single-source fraction           0.945607
  required maximum                     0.80
  hard negatives                       428 / 408 groups / 2 sources

TIRE_SQUEAL
  final assets                         11
  independent groups                   11
  hard negatives                       25 / 12 groups / 2 sources
  train                                9 / 9 groups
  validation                           0 / 0 groups
  test                                 2 / 2 groups
```

BACKGROUND remains closed at 416 assets / 383 groups / 4 source families. SIREN and VEHICLE_HORN remain coverage-complete. Asset-quality stop lines remain all zero.

## Exact detailed coverage gaps

Exactly 17 remain:

```text
FIRE_ALARM_ASSETS_BELOW_MIN
FIRE_ALARM_GROUPS_BELOW_MIN
FIRE_ALARM_TEST_ASSETS_BELOW_MIN
FIRE_ALARM_TEST_GROUPS_BELOW_MIN
FIRE_ALARM_TRAIN_ASSETS_BELOW_MIN
FIRE_ALARM_TRAIN_GROUPS_BELOW_MIN
FIRE_ALARM_VALIDATION_ASSETS_BELOW_MIN
FIRE_ALARM_VALIDATION_GROUPS_BELOW_MIN
GLASS_SHATTER_SOURCE_CONCENTRATION_TOO_HIGH
TIRE_SQUEAL_ASSETS_BELOW_MIN
TIRE_SQUEAL_GROUPS_BELOW_MIN
TIRE_SQUEAL_TEST_ASSETS_BELOW_MIN
TIRE_SQUEAL_TEST_GROUPS_BELOW_MIN
TIRE_SQUEAL_TRAIN_ASSETS_BELOW_MIN
TIRE_SQUEAL_TRAIN_GROUPS_BELOW_MIN
TIRE_SQUEAL_VALIDATION_ASSETS_BELOW_MIN
TIRE_SQUEAL_VALIDATION_GROUPS_BELOW_MIN
```

Readiness remains fail-closed with the nine coarse blockers expected for an open corpus certificate, non-PASS coverage/freezes/reproducibility and positive-count deficits in FIRE/TIRE.

## Certification lineage

```text
CERT-DOC-001..009              INVALIDATED / historical
CERT-DOC-010                   CERTIFIED / current
CERT-MK1-DF-TOOLCHAIN-004      INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005      CANDIDATE
CERT-MK1-DF-SONYC-001          CERTIFIED / scoped
CERT-MK1-DF-CORPUS-001         OPEN
```

`TOOLCHAIN-005` remains candidate because active corpus acquisition can still modify closure-era implementation/evidence. `SONYC-001` remains independently valid inside its scope.

## PR #33 acquisition boundary

PR #33 hardens Public Gap persistence to the triggering SHA, rejects durable persistence when `main` moves, adds attribution-only CC-BY-4.0 page verification, and proposes exact Wikimedia FIRE candidates.

Those changes are authorized as **candidate acquisition/tooling changes only**. Until post-merge materialization produces fresh durable evidence:

- current FIRE final count remains 9;
- coverage remains the audited 17-gap FAIL;
- CORPUS-001 remains OPEN;
- `modeling_allowed=false`;
- Benchmark A/B/C remain locked.

No documentation statement may predict post-grouping counts or pre-credit the new recording families.

## Documentation inventory

This audit is the one additional Markdown record over the 213-file DOC-009 inventory:

```text
Markdown corpus = 214 files
```

## Invalidation

`CERT-DOC-010` becomes stale if any audited durable ledger/coverage/readiness identity or count changes; if promise/taxonomy/rights/mapping/probe/fingerprint/grouping/dedup/split/coverage/freeze semantics change; if certificate state changes; if `ECHO-FREE-TIER-001` changes; or if the Markdown inventory changes without a fresh audit.
