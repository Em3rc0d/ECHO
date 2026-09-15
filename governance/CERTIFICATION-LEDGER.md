# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-007`

`CERTIFIED` is scope-bounded. Documentation never fabricates empirical evidence; green CI never compensates for stale governance; no certificate may depend on a path that violates `ECHO-FREE-TIER-001`.

## States

`OPEN` · `BLOCKED` · `CANDIDATE` · `CERTIFIED` · `INVALIDATED` · `EXTERNAL_GATE_OPEN`

## Current certificates and empirical outputs

| ID | Claim / artifact | State | Current evidence / dependency | Invalidates when |
|---|---|---|---|---|
| CERT-ECHO-000 | Immutable ECHO promise | CERTIFIED | PROJECT-CHARTER | owner changes promise |
| CERT-MK0-001..013 | MK0 decisions + research gate | CERTIFIED | MK0 evidence corpus | material ancestor changes |
| CERT-MK1-READY-001 | MK1 replay-build readiness | CERTIFIED | MK0 + Definition of Ready | architecture-changing dependency |
| CERT-MK1-DF-SPEC-001 | Data Foundry architecture/contracts/policies | CERTIFIED | Foundry docs/config/schema/foundation | semantic contract changes |
| CERT-MK1-DF-TOOLCHAIN-001..003 | Historical toolchains | INVALIDATED | historical evidence | superseded |
| CERT-MK1-DF-TOOLCHAIN-004 | SONYC persistence/fingerprint Foundry baseline | INVALIDATED | baseline `ab8c47ba...`; runs `34922010529`, `34922010518`, `34922010537` | invalidated by corpus-role-boundary semantics in PR #10 |
| CERT-MK1-DF-TOOLCHAIN-005 | Current closure-era Foundry toolchain candidate | CANDIDATE | PR #10 + PR #11 and subsequent exact CI/free-tier/cascade evidence | certify only after closure implementation stabilizes |
| CERT-MK1-DF-SONYC-001 | SONYC v2.3 full real-media materialization + fingerprint closure | CERTIFIED | run `34922010537`; durable `78fc0198...`; machine-readable certificate | SONYC evidence/materialization/fingerprint/free-tier changes |
| EMP-MK1-CORPUS-READINESS-001 | Machine-readable corpus closure readiness | BLOCKED | durable readiness `ed069c64...` | recomputed whenever evidence/policy changes |
| EMP-DATASET-001 | Exact admitted real corpus identity/counts/durations/groups | OPEN | release-safe closure | produced only from closed corpus |
| EMP-DATA-QUALITY-001 | Duplicate/quality/diversity evidence | OPEN | global dedup/group/split/coverage | produced only from real closure |
| CERT-MK1-DF-CORPUS-001 | Named release-safe frozen corpus | OPEN | dataset + quality + all closure gates + reproducibility + free-tier | source/asset/policy/mapping/group/split/fingerprint/freeze change |
| CERT-DOC-001..005 | Historical documentation certificates | INVALIDATED | historical corpora | superseded |
| CERT-DOC-006 | SONYC recertification documentation corpus | INVALIDATED | 210-file audit | superseded by corpus-role-boundary/readiness delta |
| CERT-DOC-007 | Current corpus-closure iteration documentation corpus | CERTIFIED | `DOCUMENTATION-AUDIT-2026-09-14-CORPUS-CLOSURE-ITERATION-007.md` | Markdown/readiness/policy/certification truth changes |
| EXT-CAMERA-001 | Real camera integration | EXTERNAL_GATE_OPEN | authorized field evidence | field evidence + upstream authorization |
| EMP-MODEL-001 | Model winner | BLOCKED | certified corpus + Benchmark A/B/C | cannot run before corpus cert |
| EMP-THRESH-001 | Event thresholds | BLOCKED | certified corpus + model/replay | cannot run before corpus/model gates |

## SONYC scoped certificate

`CERT-MK1-DF-SONYC-001` remains independently valid:

```text
implementation baseline  ab8c47ba6aabb25390644954a2a06945ca7a81bb
real SONYC run            34922010537
verified shards           19 / 19 PASS
probe failures            0
fingerprint failures      0
durable SONYC evidence    78fc019839f1c9dad1a58a70d439605d887361d7
```

Its scope does not certify the final corpus.

## Current closure evidence

The corpus-role boundary was merged at `b2fc09b1c98c4c8adcb2fe9dc4db7e1dadc61107` and propagated through:

```text
canonical ledger evidence  3ba3f3141a24013abf8f3cbf68f46043a149ae12
closure audits              4ebbe3f042181ec789d26d1ff4d6ede4ba656ef9
closure readiness           ed069c64d8b5efc855157531a6a59aadff363f40
```

Current corpus-facing canonical ledger:

```text
entry_count                         1081
canonical_fingerprint_count         1081
canonical_fingerprint_missing_count    0
role-boundary input_rows            1164
review-only rows removed              83
GROUPING_GLOBAL_AUDIT_REQUIRED       448
```

The 83 removed rows remain source materialization/review evidence. No content was deleted and no label/source-family/coverage credit was invented.

Positive assets / underlying source families remain:

```text
FIRE_ALARM       10 / 3
GLASS_SHATTER   304 / 2
SIREN           175 / 3
TIRE_SQUEAL      11 / 2
VEHICLE_HORN    245 / 3
```

Hard-negative assets / underlying source families remain:

```text
FIRE_ALARM       34 / 1
GLASS_SHATTER   401 / 1
SIREN            32 / 1
TIRE_SQUEAL       0 / 0
VEHICLE_HORN      0 / 0
```

Exact readiness gap codes at `ed069c64...`:

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
LEDGER_GROUPING_GLOBAL_AUDIT_REQUIRED_448
LEDGER_LICENSE_NOT_RELEASE_SAFE_1
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

## Active grouping change

PR #11 conservatively strengthens split protection: existing groups, exact identity and governed near-duplicate relations are unioned into deterministic global acoustic components. It performs no content merge/deletion and does not claim new independent source families. Split conflicts, if exposed, remain fail-closed.

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

Until then: no model training, threshold calibration, replay progression or real-camera progression.

## Dependency DAG

```text
CERT-ECHO-000 + CERT-DOC-007 + ECHO-FREE-TIER-001
        ↓
CERT-MK1-DF-SPEC-001
        ↓
TOOLCHAIN-005 = CANDIDATE
        +
CERT-MK1-DF-SONYC-001 = CERTIFIED
        ↓
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
        ↓
close dedup/group + rights/semantic conflicts + real coverage/HN deficits
        ↓
split + coverage + freeze #1/#2 + reproducibility
        ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
        ↓
CERT-MK1-DF-CORPUS-001
        ↓
model-entry → Benchmark A/B/C
```

## Invalidation

Material changes to promise, taxonomy, source/audio/event contracts, acquisition, rights/mapping/review/probe/fingerprint/coverage/dedup/group/split/freeze/handoff semantics, model-entry wiring, free-tier boundary or governing documentation require dependency review and selective recertification.
