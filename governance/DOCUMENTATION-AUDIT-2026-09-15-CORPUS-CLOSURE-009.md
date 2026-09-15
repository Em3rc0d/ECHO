# Documentation Audit — Corpus Closure Truth 009

**Certificate:** `CERT-DOC-009`  
**Status:** `CERTIFIED`  
**Audit date:** `2026-09-15`  
**Audited main:** `608ecc5efdcd399b7f29b4d522b0fb46b99e87bf`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`

## Scope

This audit rebinds ECHO documentation governance to the current durable corpus-closure evidence after the independently materialized OpenGameArt/rubberduck CC0 source was admitted, globally grouped, deduplicated, split-audited and propagated through readiness. It certifies documentation consistency only; it does **not** certify the final corpus or authorize model work.

## Immutable product direction

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

The active MK1 path remains product-critical: release-safe acoustic corpus → corpus certification → Benchmark A/B/C → model winner → Event Engine → Edge Agent → MQTT/replay → real camera. Cameras, dashboards, alerts and transports remain supporting integrations and cannot redefine the acoustic promise.

## Audited empirical truth

```text
main readiness commit            608ecc5efdcd399b7f29b4d522b0fb46b99e87bf
implementation baseline          ed00ba035dc03c345caff7dc2a1697b59e3ce13b
canonical corpus-facing rows     1123
canonical fingerprints           1123 / 1123
ledger blockers                  0
global dedup                     PASS
recording-family audit           PASS
split integrity                  PASS
protected split quarantine       3 groups / 77 assets
coverage gate                    FAIL
freeze #1 validation             FAIL
freeze #2 validation             FAIL
reproducibility                  FAIL
readiness                        BLOCKED
eligible_for_certificate_review  false
modeling_allowed                 false
CERT-MK1-DF-CORPUS-001           OPEN
readiness evidence identity      797daf518868a86ee553e4a663a4ee444df4e055c915b3d34f41fb6f8e495e11
```

OpenGameArt/rubberduck contributes real CC0 materialized evidence under one independent acoustic-origin family while its GitHub mirror remains transport-only. The corpus-facing ledger remains blocker-free and fully fingerprinted. Protected split conflicts remain visible as three quarantined complete acoustic groups (77 assets); no member is remapped.

## Audited corpus counts

```text
positive assets, pre-final-dedup ledger
FIRE_ALARM       9
GLASS_SHATTER    310
SIREN            173
TIRE_SQUEAL      11
VEHICLE_HORN     245

hard-negative assets, pre-final-dedup ledger
FIRE_ALARM       34
GLASS_SHATTER    440
SIREN            32
TIRE_SQUEAL      0
VEHICLE_HORN     0

hard-negative underlying source families
FIRE_ALARM       1
GLASS_SHATTER    2
SIREN            1
TIRE_SQUEAL      0
VEHICLE_HORN     0
```

The OpenGameArt evidence closes the former `GLASS_SHATTER` hard-negative second-source deficit at ledger/readiness level. It does not close the remaining positive-source concentration requirement for `GLASS_SHATTER`.

## Exact current readiness gaps

```text
CORPUS_CERTIFICATE_NOT_CERTIFIED
COVERAGE_GATE_GAP_CODES_NOT_EMPTY
COVERAGE_GATE_NOT_PASS
COVERAGE_GATE_STATUS_NOT_PASS
FIRE_ALARM_ASSETS_9_LT_50
FIRE_ALARM_HARD_NEGATIVE_SOURCES_1_LT_2
FREEZE_1_VALIDATION_NOT_PASS
FREEZE_2_VALIDATION_NOT_PASS
REPRODUCIBILITY_NOT_PASS
SIREN_HARD_NEGATIVE_SOURCES_1_LT_2
TIRE_SQUEAL_ASSETS_11_LT_50
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2
VEHICLE_HORN_HARD_NEGATIVES_0_LT_20
VEHICLE_HORN_HARD_NEGATIVE_SOURCES_0_LT_2
```

These are genuine closure deficits. They may only be closed by valid release-safe evidence and downstream freeze/reproducibility execution. Floors, source-family rules and semantic stop-lines remain unchanged.

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
