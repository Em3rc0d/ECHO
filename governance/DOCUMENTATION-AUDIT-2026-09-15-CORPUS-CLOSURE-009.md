# Documentation Audit — Corpus Closure Truth 009

**Certificate:** `CERT-DOC-009`  
**Status:** `CERTIFIED`  
**Audit date:** `2026-09-15`  
**Audited main:** `ecf76528d5cd722757782cc54311c3f02038b2b9`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`

## Scope

This audit rebinds ECHO documentation governance to the durable MK1 corpus-closure state after empirical BigSoundBank GLASS expansion and its downstream global grouping/split-quarantine recomputation. It certifies documentation consistency and the observed gate state only; it does **not** certify the final corpus or authorize model work.

## Immutable product direction

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

The active MK1 path remains: release-safe acoustic corpus → `CERT-MK1-DF-CORPUS-001` → Benchmark A/B/C → model winner → Event Engine → Edge Agent → MQTT/replay → real camera. Cameras, dashboards, alerts and transports remain supporting integrations.

## Audited empirical truth

```text
main readiness commit            ecf76528d5cd722757782cc54311c3f02038b2b9
public-gap evidence baseline      48e938034b98cf4d02588879b28ddec00c4666dd
canonical-ledger evidence         8ff9c53aa6ce0b286f9414f56d7590bdf2f9609a
closure evidence commit           b572d5ec1f3015dea1f010c7fd10cf30d653dc09
canonical corpus-facing rows      1158
canonical fingerprints            1158 / 1158
ledger blockers                   0
BigSoundBank ledger rows          53
global acoustic components        14
members reassigned                125
global dedup                      PASS
recording-family audit            PASS
split integrity                   PASS
protected split quarantine        2 groups / 93 assets
background                        416 assets / 383 groups / 4 sources / PASS
TIRE_SQUEAL hard negatives        25 assets / 12 groups / 2 sources / PASS
coverage gate                     FAIL
coverage detailed gap codes       17
freeze #1 validation              FAIL
freeze #2 validation              FAIL
reproducibility                   FAIL
readiness                         BLOCKED
readiness coarse gap codes        9
eligible_for_certificate_review   false
modeling_allowed                  false
CERT-MK1-DF-CORPUS-001            OPEN
readiness evidence identity       9e7325ad5790a6a1448a2a8cbceb0f314ef1cbf7164c9079e65313a405bf2ce8
```

The corpus-facing ledger is blocker-free and fully fingerprinted. Global grouping performs no content deletion or content merge.

## Empirical GLASS result

Nine additional governed BigSoundBank `GLASBrk` candidates materialized and entered the pre-final ledger, moving pre-final `GLASS_SHATTER` positives from 310 to 319. Global acoustic grouping then revealed a larger protected cross-source component. The split policy correctly quarantined complete conflicting groups rather than manually remapping members.

Final coverage is therefore:

```text
GLASS_SHATTER final assets       238
independent groups               221
BIGSOUNDBANK                       6
FREESOUND                        226
OPENGAMEART_RUBBERDUCK             6
max single-source fraction   0.94958
required maximum               0.80
```

The new evidence did **not** justify removing or hiding acoustically linked rows merely to improve coverage. The observed quarantine increased to 93 assets and remains authoritative.

## Current positive and hard-negative ledger counts

```text
positive assets, pre-final ledger
FIRE_ALARM         9
GLASS_SHATTER    319
SIREN             173
TIRE_SQUEAL        11
VEHICLE_HORN      245

hard-negative assets, pre-final ledger
FIRE_ALARM       206
GLASS_SHATTER    440
SIREN            245
TIRE_SQUEAL       25
VEHICLE_HORN     146

hard-negative underlying source families
FIRE_ALARM         4
GLASS_SHATTER      2
SIREN              4
TIRE_SQUEAL        2
VEHICLE_HORN       3
```

All target-specific hard-negative floors are now closed. `TIRE_SQUEAL` HN remains 25 assets / 12 groups / 2 sources after final coverage handling.

## Background remains closed

```text
assets             416
groups             383
source families      4

BIGSOUNDBANK
OPENGAMEART_RUBBERDUCK
SONYC_UST
WIKIMEDIA_COMMONS
```

## Final detailed coverage blockers

Exactly **17** detailed gaps remain:

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

Coverage asset quality remains clean: zero unknown licenses, zero missing label provenance, zero non-positive durations, zero invalid probes, zero exact duplicate groups and zero near-duplicate groups.

## Exact readiness gaps

Readiness remains correctly coarser than detailed coverage and contains **9** blockers:

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

The remaining empirical work is strictly positive-class closure: reduce `GLASS_SHATTER` source concentration with genuine non-Freesound positives, increase `FIRE_ALARM` positives/groups/split coverage, and increase `TIRE_SQUEAL` positives/groups/split coverage. No floor, source-family identity or split protection may be weakened to make these gaps disappear.

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

No Benchmark A/B/C, model training, threshold calibration, replay progression or real camera certification may begin while `CERT-MK1-DF-CORPUS-001 != CERTIFIED` or `modeling_allowed != true`. Hard-negative closure does not authorize model entry; Freeze #1, freeze #2 and reproducibility remain downstream of coverage.

## Markdown inventory

Expected repository Markdown count remains **213**.

## Invalidation

`CERT-DOC-009` becomes stale when audited Markdown inventory, promise, free-tier policy, taxonomy, rights/admission semantics, ledger identity, grouping/dedup/split/coverage/freeze/reproducibility evidence, certificate state or model-entry law changes materially.
