# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-006`

`CERTIFIED` is always scope-bounded. Documentation never fabricates empirical evidence; green CI never compensates for stale governance; no certificate may depend on a path that violates `ECHO-FREE-TIER-001`.

## States

`OPEN` · `BLOCKED` · `CANDIDATE` · `CERTIFIED` · `INVALIDATED` · `EXTERNAL_GATE_OPEN`

## Current certificates and empirical outputs

| ID | Claim / artifact | State | Current evidence / dependency | Invalidates when |
|---|---|---|---|---|
| CERT-ECHO-000 | Immutable ECHO promise | CERTIFIED | PROJECT-CHARTER | owner changes promise |
| CERT-MK0-001..012 | MK0 scoped research/design decisions | CERTIFIED | MK0 evidence corpus | material upstream fact/decision changes |
| CERT-MK0-013 | MK0 research gate | CERTIFIED | CERT-MK0-001..012 | any MK0 ancestor invalidates |
| CERT-MK1-READY-001 | MK1 replay-build readiness | CERTIFIED | MK0 + Definition of Ready | architecture-changing dependency |
| CERT-MK1-DF-SPEC-001 | Data Foundry architecture/contracts/policies | CERTIFIED | Foundry docs/config/schema/foundation | semantic contract changes |
| CERT-MK1-DF-TOOLCHAIN-001 | Historical toolchain | INVALIDATED | old baseline `2c4d4c2...` | superseded |
| CERT-MK1-DF-TOOLCHAIN-002 | Historical toolchain | INVALIDATED | baseline `be75a432...`, run `34800084225` | superseded |
| CERT-MK1-DF-TOOLCHAIN-003 | Historical readiness/model-entry toolchain | INVALIDATED | baseline `dc225803...`, run `34904125873` | superseded by SONYC fingerprint/persistence changes |
| CERT-MK1-DF-TOOLCHAIN-004 | Current Data Foundry + SONYC persistence/fingerprint toolchain | CERTIFIED | baseline `ab8c47ba...`; Foundry CI `34922010529`; Free-Tier `34922010518`; SONYC `34922010537` | governed Foundry/workflow/test semantics change |
| CERT-MK1-DF-SONYC-001 | SONYC v2.3 full real-media materialization + canonical fingerprint closure | CERTIFIED | run `34922010537`; durable evidence `78fc0198...`; machine-readable certificate | SONYC evidence/materialization/fingerprint/free-tier contract changes |
| EMP-MK1-CORPUS-READINESS-001 | Machine-readable corpus closure readiness | BLOCKED | readiness `de1d31b2...` | recomputed whenever input evidence/policy changes |
| EMP-DATASET-001 | Exact admitted real corpus identity/counts/durations/groups | OPEN | real release-safe closure | produced only from closed corpus |
| EMP-DATA-QUALITY-001 | Duplicate/quality/diversity evidence | OPEN | global dedup/group/split/coverage evidence | produced only from real closure |
| CERT-MK1-DF-CORPUS-001 | Named release-safe frozen corpus | OPEN | EMP-DATASET-001 + EMP-DATA-QUALITY-001 + all DF closure gates + reproducibility + free-tier PASS | source/asset/policy/mapping/group/split/fingerprint/freeze change |
| CERT-DOC-001..004 | Historical documentation certificates | INVALIDATED | historical corpora | superseded |
| CERT-DOC-005 | Historical 208-file documentation corpus | INVALIDATED | corpus-readiness audit | superseded by SONYC/toolchain recertification delta |
| CERT-DOC-006 | Current 210-file documentation corpus | CERTIFIED | `DOCUMENTATION-AUDIT-2026-09-14-SONYC-RECERTIFICATION.md` | Markdown/policy/certification truth changes without audit |
| EXT-CAMERA-001 | Real camera integration | EXTERNAL_GATE_OPEN | authorized camera/site evidence | closes only with field evidence and upstream authorization |
| EMP-MODEL-001 | Model winner | BLOCKED | certified corpus + Benchmark A/B/C | cannot run before corpus cert |
| EMP-THRESH-001 | Classifier/Event Engine thresholds | BLOCKED | certified corpus + validation/replay | cannot run before corpus/model gates |
| EMP-DIST-001 | Distance/SNR envelope | BLOCKED | authorized field tests | external + upstream gates |
| EMP-CAP-001 | Multi-source capacity envelope | OPEN | future runtime load/soak | runtime evidence changes |
| EMP-SLO-001 | Final MK1/MK2 SLO evidence | OPEN | runtime/quality/field evidence | evidence changes |

## Current Data Foundry recertification

```text
implementation baseline  ab8c47ba6aabb25390644954a2a06945ca7a81bb
Data Foundry CI           34922010529  PASS / Python 3.10, 3.11, 3.12
Free-Tier Boundary        34922010518  PASS
Documentation Governance  34922010525  PASS on pre-recertification docs
real SONYC run            34922010537  PASS
```

The real SONYC run passed 19/19 shards, merge, canonical fingerprint contract and durable persistence. Evidence was committed at `78fc019839f1c9dad1a58a70d439605d887361d7`, then propagated through canonical ledger `c93ddb97902b3650921426aaf841473245c7908d`, closure audits `311cc2001931d4cceedb90ab5d21f06e15fdf881`, and readiness `de1d31b280e9fad4a3764537aa75d7d72802adb7`.

## SONYC scoped certificate

Authoritative record: `MK1/mining-site/materialization/sonyc-v2.3-materialization-certificate.json`.

```text
source release assets              18510
source release duration seconds    185100.0
verified shards                    19 / 19
target candidate rows              236
confuser candidate rows            428
fingerprinted ledger assets        599
probe failures                       0
fingerprint failures                 0
```

`CERT-MK1-DF-SONYC-001` does not imply final corpus admission or model authorization.

## Current corpus readiness truth

Authoritative readiness is `BLOCKED`:

```text
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
```

The canonical ledger summary now has complete canonical fingerprint coverage:

```text
entry_count = 1164
canonical_fingerprint_count = 1164
canonical_fingerprint_missing_count = 0
status = PASS_CONSOLIDATED_WITH_OPEN_GATES
```

Pre-final positive assets / underlying source families:

```text
FIRE_ALARM       10 / 3
GLASS_SHATTER   304 / 2
SIREN           175 / 3
TIRE_SQUEAL      11 / 2
VEHICLE_HORN    245 / 3
```

Hard-negative assets / underlying source families:

```text
FIRE_ALARM       34 / 1
GLASS_SHATTER   401 / 1
SIREN            32 / 1
TIRE_SQUEAL       0 / 0
VEHICLE_HORN      0 / 0
```

Exact readiness gap codes:

```text
CORPUS_CERTIFICATE_NOT_CERTIFIED
COVERAGE_GATE_GAP_CODES_NOT_EMPTY
COVERAGE_GATE_NOT_PASS
COVERAGE_GATE_STATUS_NOT_PASS
FIRE_ALARM_ASSETS_10_LT_50
FIRE_ALARM_HARD_NEGATIVE_SOURCES_1_LT_2
FREEZE_1_VALIDATION_NOT_PASS
FREEZE_2_VALIDATION_NOT_PASS
GLASS_SHATTER_HARD_NEGATIVE_SOURCES_1_LT_2
GLOBAL_DEDUP_AUDIT_NOT_PASS
LEDGER_AUGMENTATION_ONLY_NO_REAL_SOURCE_CREDIT_4
LEDGER_GROUPING_GLOBAL_AUDIT_REQUIRED_503
LEDGER_LICENSE_NOT_RELEASE_SAFE_1
LEDGER_NO_EXACT_SEMANTIC_ROLE_83
LEDGER_RIGHTS_TEXT_CONFLICT_REVIEW_REQUIRED_1
LEDGER_SEMANTIC_STATUS_CONFLICT_FIRE_ALARM_1
LEDGER_SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL_1
RECORDING_FAMILY_AUDIT_NOT_PASS
REPRODUCIBILITY_NOT_PASS
SIREN_HARD_NEGATIVE_SOURCES_1_LT_2
SPLIT_INTEGRITY_NOT_PASS
TIRE_SQUEAL_ASSETS_11_LT_50
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2
VEHICLE_HORN_HARD_NEGATIVES_0_LT_20
VEHICLE_HORN_HARD_NEGATIVE_SOURCES_0_LT_2
```

## Release law

```text
CERT-MK1-DF-CORPUS-001 = CERTIFIED
AND gap_codes=[]
AND required closure evidence = PASS
AND reproducibility = PASS
AND ECHO-FREE-TIER-001 = PASS
        ↓
model-entry gate PASS
        ↓
Benchmark A/B/C authorized
```

Without it there is no model training, threshold calibration, replay progression or real-camera progression.

## Documentation lineage

```text
CERT-DOC-001..005  historical / invalidated
CERT-DOC-006       current / CERTIFIED / 210 Markdown files
```

## Dependency DAG

```text
CERT-ECHO-000
  + CERT-DOC-006
  + ECHO-FREE-TIER-001
          ↓
CERT-MK1-DF-SPEC-001
          ↓
CERT-MK1-DF-TOOLCHAIN-004
          +
CERT-MK1-DF-SONYC-001
          ↓
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
          ↓
close ledger blockers + global audits + split + coverage + freeze×2 + reproducibility
          ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
          ↓
CERT-MK1-DF-CORPUS-001
          ↓
model-entry gate → Benchmark A/B/C → EMP-MODEL-001
```

## Invalidation

A material change to promise, taxonomy, schemas, source/audio/event contracts, source/acquisition registry, rights/mapping/review/probe/fingerprint/coverage/dedup/group/split/freeze/handoff semantics, SONYC persistence, model-entry guard, benchmark set, delivery/privacy policy, zero-cost execution boundary or governing documentation requires dependency review and selective recertification.
