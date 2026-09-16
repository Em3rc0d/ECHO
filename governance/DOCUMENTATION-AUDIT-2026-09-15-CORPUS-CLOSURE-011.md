# Documentation Audit — MK1 Corpus Closure 011

**Certificate:** `CERT-DOC-011`  
**Status:** `CERTIFIED`  
**Audit date:** 2026-09-15  
**Durable readiness commit:** `2088c93d65b5d4dff58bb5cdb91b0e76e6288afb`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`

## Scope

This audit supersedes `CERT-DOC-010` and binds documentation governance to the durable post-Wikimedia FIRE acquisition cascade.

It certifies only the evidence that survived real-byte materialization, canonical-ledger reconstruction, global grouping/dedup, protected split quarantine, final coverage evaluation and readiness recomputation. Future Freesound FIRE/TIRE candidates receive zero credit until the same chain completes again.

## Immutable product promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

The critical path remains corpus → corpus certificate → Benchmark A/B/C → model winner → Event Engine → Edge Agent → MQTT/replay → real camera.

## Durable evidence audited

At `main@2088c93d65b5d4dff58bb5cdb91b0e76e6288afb`:

```text
canonical ledger baseline              0e05b9ce7ef9afdbd6d0d327922f9811fa0a50d7
canonical ledger entries               1162
canonical fingerprints                 1162 / 1162
canonical fingerprint missing          0
ledger blockers                        0
ledger sha256                          b250b18e8ccef3776cdc38d42f240a057bcf99b260cc6cb58a77aad93e9d0cab

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
9b6da43da378dbf546a3961c6ed47b8e7218b5135bbe84680f58eecf86030559
```

## Current target truth

```text
FIRE_ALARM
  final assets                         12
  independent groups                   9
  duration                             311.05767 s
  positive source families             3
    BIGSOUNDBANK                        4 assets
    FREESOUND                           5 assets
    WIKIMEDIA_COMMONS                   3 assets
  train                                10 / 7 groups
  validation                           2 / 2 groups
  test                                 0 / 0 groups
  hard negatives                       206 / 206 groups / 4 sources

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
  duration                             280.544098 s
  train                                9 / 9 groups
  validation                           0 / 0 groups
  test                                 2 / 2 groups
  hard negatives                       25 / 12 groups / 2 sources
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

Readiness remains fail-closed with nine coarse blockers. The FIRE positive precheck now reports `FIRE_ALARM_ASSETS_12_LT_50`; TIRE remains `TIRE_SQUEAL_ASSETS_11_LT_50`.

## Empirical change since DOC-010

Three real Wikimedia FIRE recordings survived the complete chain rather than receiving configuration-only credit:

```text
FIRE final assets        9  → 12
FIRE final groups        6  → 9
FIRE source families     2  → 3
FIRE train assets        7  → 10
FIRE train groups        4  → 7
FIRE duration            190.18 s → 311.06 s
```

No coverage floor was lowered and no quarantine was hidden. The 17 gap-code identities remain unchanged because no threshold was crossed yet.

## Freesound persistence/orchestration boundary

The next authorized acquisition path is Freesound FIRE/TIRE. Its generated evidence must be bound to the workflow trigger SHA and rejected if `main` moves. Workflow YAML changes themselves must not self-trigger expensive materialization, and the raw supplemental semantic config must not launch canonical-ledger reconstruction before fresh materialization evidence exists.

Therefore:

- Release-safe Freesound materialization is the sole automatic materializer triggered by `freesound_cc0_supplemental.v1.json` changes.
- The narrower CC0 workflow remains manually/script-evidence triggerable but does not race the release-safe path on supplemental edits.
- Canonical Ledger consumes the durable Freesound evidence report / successful materialization workflow, not the raw supplemental config push.
- Future candidates remain zero-credit until the durable cascade recomputes final coverage.

## Certification lineage

```text
CERT-DOC-001..010              INVALIDATED / historical
CERT-DOC-011                   CERTIFIED / current
CERT-MK1-DF-TOOLCHAIN-004      INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005      CANDIDATE
CERT-MK1-DF-SONYC-001          CERTIFIED / scoped
CERT-MK1-DF-CORPUS-001         OPEN
```

## Documentation inventory

```text
Markdown corpus = 215 files
```

## Invalidation

`CERT-DOC-011` becomes stale if any audited ledger/coverage/readiness identity or count changes; if promise/taxonomy/rights/mapping/probe/fingerprint/grouping/dedup/split/coverage/freeze semantics change; if certificate state changes; if `ECHO-FREE-TIER-001` changes; or if the Markdown inventory changes without a fresh audit.
