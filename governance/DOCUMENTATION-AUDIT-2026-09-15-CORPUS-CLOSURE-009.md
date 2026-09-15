# Documentation Audit — Corpus Closure Truth 009

**Certificate:** `CERT-DOC-009`  
**Status:** `CERTIFIED`  
**Audit date:** `2026-09-15`  
**Audited main:** `abd49a196b4d7fd96725fef9196f778c19ed4819`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`

## Scope

This audit rebinds ECHO documentation governance to the durable MK1 corpus-closure state after the governed Wikimedia Commons confuser admission closed the third-background-source deficit. It certifies documentation consistency and the observed gate state only; it does **not** certify the final corpus or authorize model work.

The acquisition path was executed as real evidence, not as a source-count metadata patch:

```text
CC0 Wikimedia page
→ public audio bytes
→ SHA-256
→ ffprobe
→ canonical audio fingerprint
→ explicit FIRE_ALARM/SIREN hard-negative role
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
main readiness commit            abd49a196b4d7fd96725fef9196f778c19ed4819
public-gap evidence commit       64e755f08cae3c17f52e9dcf91709ad2b8aa9c2c
canonical-ledger evidence        b8a27b9a523dbda4d8abbb0bb81369bebb16f901
closure evidence commit          2ca6f7671cad4fb183956cb7b9562f01e3804e97
canonical corpus-facing rows     1124
canonical fingerprints           1124 / 1124
ledger blockers                  0
global dedup                     PASS
recording-family audit           PASS
split integrity                  PASS
protected split quarantine       3 groups / 77 assets
background                       391 assets / 371 groups / 3 sources / PASS
coverage gate                    FAIL
coverage detailed gap codes      20
freeze #1 validation             FAIL
freeze #2 validation             FAIL
reproducibility                  FAIL
readiness                        BLOCKED
eligible_for_certificate_review  false
modeling_allowed                 false
CERT-MK1-DF-CORPUS-001           OPEN
readiness evidence identity      87ac42503bad478d2068a967bdbc701f941576a2cb138a20692b95cff881d686
```

The corpus-facing ledger remains blocker-free and fully fingerprinted. Protected split conflicts remain visible as three quarantined complete acoustic groups (77 assets); no member is remapped. Global grouping still performs no content deletion or content merge.

## Wikimedia background closure

One self-recorded CC0 Wikimedia Commons electronic-doorbell asset is admitted under the already-frozen `WIKIMEDIA_COMMONS` underlying acoustic-origin family. It remains target-free and receives only explicit hard-negative roles for `FIRE_ALARM` and `SIREN`; it is never promoted to an ECHO positive.

After global grouping, deduplication and protected split handling, final release-safe background is:

```text
assets              391
groups              371
source families     3

OPENGAMEART_RUBBERDUCK
SONYC_UST
WIKIMEDIA_COMMONS
```

`BACKGROUND_SOURCES_BELOW_MIN` is absent from the final coverage gate. The detailed coverage set therefore fell from **21 → 20** without lowering the `min_sources=3` floor or inventing a source family.

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
TIRE_SQUEAL      0
VEHICLE_HORN     146

hard-negative underlying source families
FIRE_ALARM       4
GLASS_SHATTER    2
SIREN            4
TIRE_SQUEAL      0
VEHICLE_HORN     3
```

No positive-class count changed as a side effect of the Wikimedia admission. The new asset only adds governed target-specific negative evidence plus one legitimate background source family.

## Final detailed coverage blockers

Exactly 20 detailed coverage gaps remain:

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
TIRE_SQUEAL_HARD_NEGATIVE_ASSETS_BELOW_MIN
TIRE_SQUEAL_HARD_NEGATIVE_GROUPS_BELOW_MIN
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_BELOW_MIN
TIRE_SQUEAL_TEST_ASSETS_BELOW_MIN
TIRE_SQUEAL_TEST_GROUPS_BELOW_MIN
TIRE_SQUEAL_TRAIN_ASSETS_BELOW_MIN
TIRE_SQUEAL_TRAIN_GROUPS_BELOW_MIN
TIRE_SQUEAL_VALIDATION_ASSETS_BELOW_MIN
TIRE_SQUEAL_VALIDATION_GROUPS_BELOW_MIN
```

Coverage asset quality remains clean: zero unknown licenses, zero missing label provenance, zero non-positive durations, zero invalid audio probes, zero exact duplicate groups and zero near-duplicate groups.

## Exact current readiness gaps

Readiness remains correctly coarser than final coverage and contains 11 blockers:

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
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2
```

The remaining empirical work is therefore localized to real release-safe FIRE/TIRE/GLASS acquisition and resulting split/coverage closure. Only after final coverage reaches `PASS / gap_codes=[]` may Freeze #1, Freeze #2 and reproducibility close and `CERT-MK1-DF-CORPUS-001` become eligible for certification review.

## Orchestration stop-line

The first push containing the new Canonical Ledger workflow also launched one pre-materialization ledger execution. It failed exactly at the fail-closed admission boundary because the Wikimedia report did not yet exist and wrote no durable ledger evidence. The authoritative path subsequently ran in the intended order and passed:

```text
Public Gap Materialization PASS
→ canonical ledger deterministic rebuild PASS
→ closure evidence deterministic rebuild PASS
→ readiness deterministic rebuild PASS
```

The stabilization patch removes the Canonical Ledger workflow's self-trigger path. Wikimedia/data admissions remain serialized behind successful materialization `workflow_run` events, while `workflow_dispatch` remains available for deliberate workflow-only validation.

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
