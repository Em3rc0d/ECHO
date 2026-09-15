# Documentation Audit — Corpus Closure Truth 009

**Certificate:** `CERT-DOC-009`  
**Status:** `CERTIFIED`  
**Audit date:** `2026-09-15`  
**Audited main:** `32eb3c4ee989a45fa94210a214a0f7817c1b327a`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`

## Scope

This audit rebinds ECHO documentation governance to the durable MK1 corpus-closure state after the governed BigSoundBank + Wikimedia/PDSounds acquisition closed the complete `TIRE_SQUEAL` hard-negative floor. It certifies documentation consistency and the observed gate state only; it does **not** certify the final corpus or authorize model work.

The acquisition was executed as real release-safe evidence:

```text
versioned source configs
→ public license pages
→ real public audio bytes
→ SHA-256
→ ffprobe
→ canonical audio fingerprints
→ exact governed TIRE_SQUEAL hard-negative semantics
→ canonical ledger
→ global grouping/dedup
→ protected split assignment/quarantine
→ coverage
→ readiness
```

## Immutable product direction

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

The active MK1 path remains product-critical: release-safe acoustic corpus → corpus certification → Benchmark A/B/C → model winner → Event Engine → Edge Agent → MQTT/replay → real camera. Cameras, dashboards, alerts and transports remain supporting integrations and cannot redefine the acoustic promise.

## Audited empirical truth

```text
main readiness commit            32eb3c4ee989a45fa94210a214a0f7817c1b327a
data candidate merge             dba0aeac6c628bdf6d628e70bdfecfad46515a51
public-gap evidence commit       25a5896a5f21f648408555c120403abbcbef9232
canonical-ledger evidence        01f6a91e1ead45211a35fb96cb2d6e176476c99f
closure evidence commit          58b701502dbafef3b1cc84b68988177d8b32e79c
canonical corpus-facing rows     1149
canonical fingerprints           1149 / 1149
ledger blockers                  0
global dedup                     PASS
recording-family audit           PASS
split integrity                  PASS
protected split quarantine       3 groups / 77 assets
background                       416 assets / 383 groups / 4 sources / PASS
TIRE_SQUEAL hard negatives       25 assets / 12 groups / 2 sources / PASS
coverage gate                    FAIL
coverage detailed gap codes      17
freeze #1 validation             FAIL
freeze #2 validation             FAIL
reproducibility                  FAIL
readiness                        BLOCKED
readiness coarse gap codes       9
eligible_for_certificate_review  false
modeling_allowed                 false
CERT-MK1-DF-CORPUS-001           OPEN
readiness evidence identity      ecacac93a64604a55d51c7dc1b8d2853f9a1f5f7aebbb086b8c69d93109af320
```

The corpus-facing ledger remains blocker-free and fully fingerprinted. Protected split conflicts remain visible as three quarantined complete acoustic groups (77 assets); no member is remapped. Global grouping still performs no content deletion or content merge.

## TIRE_SQUEAL hard-negative closure

The acquisition materialized **60 / 60** public-gap assets with **0 failures** and **60 canonical fingerprints**. The artifact candidate bytes were `53,083,038`, below the free-tier preferred maximum of `104,857,600` bytes. Raw media remains ephemeral; only evidence is durable in the repository.

The new TIRE hard-negative evidence uses two already-governed underlying acoustic-origin families:

```text
BIGSOUNDBANK
WIKIMEDIA_COMMONS
```

BigSoundBank rows use only semantics already frozen by `MK1-HARD-NEGATIVE-MAPPING-001`: `Car`, `Car_passing_by`, `Accelerating_and_revving_and_vroom`, and `Squeak`. Wikimedia/PDSounds contributes independent public-domain car recordings. None of these rows is promoted to a TIRE positive.

The BigSoundBank 50 km/h multi-file series deliberately remains one recording family. After global grouping, deduplication and protected split handling, final TIRE hard-negative coverage is:

```text
assets              25   >= 20  PASS
groups              12   >= 10  PASS
source families      2   >= 2   PASS
```

The following detailed coverage gaps are therefore closed and must not reappear:

```text
TIRE_SQUEAL_HARD_NEGATIVE_ASSETS_BELOW_MIN
TIRE_SQUEAL_HARD_NEGATIVE_GROUPS_BELOW_MIN
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_BELOW_MIN
```

The corresponding coarse readiness blockers are also absent:

```text
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2
```

This reduced detailed coverage gaps from **20 → 17** and coarse readiness gaps from **11 → 9** without changing any coverage floor, source-family identity, positive label or certification rule.

## Audited corpus counts

```text
positive assets, pre-final-dedup ledger
FIRE_ALARM       9
GLASS_SHATTER    310
SIREN            173
TIRE_SQUEAL      11
VEHICLE_HORN     245

hard-negative assets, pre-final-dedup ledger
FIRE_ALARM       206
GLASS_SHATTER    440
SIREN            245
TIRE_SQUEAL      25
VEHICLE_HORN     146

hard-negative underlying source families
FIRE_ALARM       4
GLASS_SHATTER    2
SIREN            4
TIRE_SQUEAL      2
VEHICLE_HORN     3
```

No positive-class count changed as a side effect of the TIRE hard-negative acquisition.

## Background remains closed

The target-free release-safe background pool now includes the newly admitted confusers and remains above its frozen source-family floor:

```text
assets              416
groups              383
source families     4

BIGSOUNDBANK
OPENGAMEART_RUBBERDUCK
SONYC_UST
WIKIMEDIA_COMMONS
```

`BACKGROUND_SOURCES_BELOW_MIN` remains absent.

## Final detailed coverage blockers

Exactly **17** detailed coverage gaps remain:

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

Coverage asset quality remains clean: zero unknown licenses, zero missing label provenance, zero non-positive durations, zero invalid audio probes, zero exact duplicate groups and zero near-duplicate groups.

## Exact current readiness gaps

Readiness remains correctly coarser than final coverage and contains **9** blockers:

```text
CORPUS_CERTIFICATE_NOT_CERTIFIED
COVERAGE_GATE_GAP_CODES_NOT_EMPTY
COVERAGE_GATE_NOT_PASS
COVERAGE_GATE_STATUS_NOT_PASS
FIRE_ALARM_ASSETS_9_LT_50
FREEZE_1_VALIDATION_NOT_PASS
FREEZE_2_VALIDATION_NOT_PASS
REPRODUCIBILITY_NOT_PASS
TIRE_SQUEAL_ASSETS_11_LT_50
```

The remaining empirical work is now strictly positive-class acquisition/split closure for `FIRE_ALARM` and `TIRE_SQUEAL`, plus reducing `GLASS_SHATTER` single-source concentration with real non-Freesound positives. Only after final coverage reaches `PASS / gap_codes=[]` may Freeze #1, Freeze #2 and reproducibility close and `CERT-MK1-DF-CORPUS-001` become eligible for certification review.

## Certificate lineage

```text
CERT-DOC-001..008            INVALIDATED / historical
CERT-DOC-009                 CERTIFIED
CERT-MK1-DF-SONYC-001        CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004    INVALIDATED / historical
CERT-MK1-DF-TOOLCHAIN-005    CANDIDATE
CERT-MK1-DF-CORPUS-001       OPEN
```

`TOOLCHAIN-005` stays CANDIDATE while corpus-closure acquisition/semantics remain active. `SONYC-001` remains scoped and independently valid.

## Direction guardrail

No work may jump ahead to model benchmarking, threshold calibration, replay progression or real-camera certification while `CERT-MK1-DF-CORPUS-001 != CERTIFIED` or `modeling_allowed != true`. Supporting infrastructure is allowed only when it directly unblocks the frozen MK1 vertical and does not displace corpus/model critical-path work.

## Markdown inventory

Expected repository Markdown count remains **213**.

## Invalidation

`CERT-DOC-009` becomes stale when audited Markdown inventory, promise, free-tier policy, taxonomy, rights/admission semantics, ledger identity, grouping/dedup/split/coverage/freeze/reproducibility evidence, certificate state or model-entry law changes materially.
