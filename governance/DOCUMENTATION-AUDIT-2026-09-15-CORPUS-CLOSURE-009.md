# Documentation Audit — Corpus Closure Truth 009

**Certificate:** `CERT-DOC-009`  
**Status:** `CERTIFIED`  
**Audit date:** `2026-09-15`  
**Audited main:** `8b478cd34184b6b8cdbee024c342eef2f497556f`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`

## Scope

This audit rebinds ECHO documentation governance to the current durable corpus-closure evidence after the OpenGameArt/rubberduck CC0 admission and the governed cross-target hard-negative accounting correction were propagated through the canonical ledger, closure evidence and readiness. It certifies documentation consistency only; it does **not** certify the final corpus or authorize model work.

## Immutable product direction

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

The active MK1 path remains product-critical: release-safe acoustic corpus → corpus certification → Benchmark A/B/C → model winner → Event Engine → Edge Agent → MQTT/replay → real camera. Cameras, dashboards, alerts and transports remain supporting integrations and cannot redefine the acoustic promise.

## Audited empirical truth

```text
main readiness commit            8b478cd34184b6b8cdbee024c342eef2f497556f
implementation baseline          e9202f4bdf1e2c6e39fc447bb1055f23273f0c5f
canonical corpus-facing rows     1123
canonical fingerprints           1123 / 1123
ledger blockers                  0
global dedup                     PASS
recording-family audit           PASS
split integrity                  PASS
protected split quarantine       3 groups / 77 assets
coverage gate                    FAIL
coverage detailed gap codes      21
freeze #1 validation             FAIL
freeze #2 validation             FAIL
reproducibility                  FAIL
readiness                        BLOCKED
eligible_for_certificate_review  false
modeling_allowed                 false
CERT-MK1-DF-CORPUS-001           OPEN
readiness evidence identity      33c57393f497b3c36b5ba66e2bf6a5db18b5f4e09851d5fc89dcf47b0858e3e0
```

OpenGameArt/rubberduck contributes real CC0 materialized evidence under one independent acoustic-origin family while its GitHub mirror remains transport-only. Governed cross-target hard-negative roles are now counted target-specifically without turning a positive for target A into a hard negative for the same target A. The corpus-facing ledger remains blocker-free and fully fingerprinted. Protected split conflicts remain visible as three quarantined complete acoustic groups (77 assets); no member is remapped.

## Audited corpus counts

```text
positive assets, pre-final-dedup ledger
FIRE_ALARM       9
GLASS_SHATTER    310
SIREN            173
TIRE_SQUEAL      11
VEHICLE_HORN     245

hard-negative assets, pre-final-dedup ledger
FIRE_ALARM       205
GLASS_SHATTER    440
SIREN            244
TIRE_SQUEAL      0
VEHICLE_HORN     146

hard-negative underlying source families
FIRE_ALARM       3
GLASS_SHATTER    2
SIREN            3
TIRE_SQUEAL      0
VEHICLE_HORN     3
```

The governed cross-target correction closes the former hard-negative deficits for `FIRE_ALARM`, `SIREN` and `VEHICLE_HORN` without changing any floor, license rule, source-family rule or positive label. It does not close `TIRE_SQUEAL` hard negatives, `FIRE_ALARM`/`TIRE_SQUEAL` positive coverage, `GLASS_SHATTER` source concentration or the third-background-source requirement in the detailed coverage gate.

## Exact current readiness gaps

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

These are the coarse readiness blockers. The final coverage gate remains stricter and currently carries 21 detailed gap codes, including background source diversity, `GLASS_SHATTER` source concentration, per-split FIRE/TIRE floors and TIRE hard-negative floors. They may only be closed by valid release-safe evidence and downstream freeze/reproducibility execution. Floors, source-family rules and semantic stop-lines remain unchanged.

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
