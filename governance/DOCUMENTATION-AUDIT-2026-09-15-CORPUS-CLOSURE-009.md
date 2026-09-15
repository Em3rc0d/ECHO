# Documentation Audit — Corpus Closure Truth 009

**Certificate:** `CERT-DOC-009`  
**Status:** `CERTIFIED`  
**Audit date:** `2026-09-15`  
**Audited main:** `d94eff2958bbe57076610524cbb192d14ec95739`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`

## Scope

This audit rebinds ECHO documentation governance to the durable post-PR #15 corpus-closure evidence. It certifies documentation consistency only; it does **not** certify the final corpus or authorize model work.

## Immutable product direction

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

The active MK1 path remains product-critical: release-safe acoustic corpus → corpus certification → Benchmark A/B/C → model winner → Event Engine → Edge Agent → MQTT/replay → real camera. Cameras, dashboards, alerts and transports remain supporting integrations and cannot redefine the acoustic promise.

## Audited empirical truth

```text
main readiness commit            d94eff2958bbe57076610524cbb192d14ec95739
implementation baseline          4b261bd10d6578a6256fca8ec848ea1055c24b32
canonical corpus-facing rows     1078
canonical fingerprints           1078 / 1078
ledger blockers                  0
global dedup                     PASS
recording-family audit           PASS
split integrity                  PASS
coverage gate                    FAIL
freeze #1 validation             FAIL
freeze #2 validation             FAIL
reproducibility                  FAIL
readiness                        BLOCKED
eligible_for_certificate_review  false
modeling_allowed                 false
CERT-MK1-DF-CORPUS-001           OPEN
readiness evidence identity      90f2dd006cfbacfe9dc1bdc5cb81c7d9411ccf5322d6ca2dd53f334e76c209e8
```

The three previously documented row blockers are no longer corpus-facing. Protected split conflicts remain visible as three quarantined complete acoustic groups (62 assets), while `split-integrity.json` is now PASS because quarantine is policy-governed and no member is remapped.

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
GLASS_SHATTER_HARD_NEGATIVE_SOURCES_1_LT_2
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

This audit adds one Markdown file to the previously audited 212-file corpus. Expected repository Markdown count after this audit: **213**.

## Invalidation

`CERT-DOC-009` becomes stale when audited Markdown inventory, promise, free-tier policy, taxonomy, rights/admission semantics, ledger identity, grouping/dedup/split/coverage/freeze/reproducibility evidence, certificate state or model-entry law changes materially.