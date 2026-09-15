# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-009`

`CERTIFIED` is scope-bounded. Green CI is execution evidence, not a substitute for missing empirical evidence. No certificate may depend on a path that violates `ECHO-FREE-TIER-001`.

## States

`OPEN` · `BLOCKED` · `CANDIDATE` · `CERTIFIED` · `INVALIDATED` · `EXTERNAL_GATE_OPEN`

## Current certificates and empirical outputs

| ID | Claim / artifact | State | Current evidence / dependency | Invalidates when |
|---|---|---|---|---|
| CERT-ECHO-000 | Immutable ECHO promise | CERTIFIED | PROJECT-CHARTER | owner changes promise |
| CERT-MK0-001..013 | MK0 decisions + research gate | CERTIFIED | MK0 evidence corpus | material ancestor changes |
| CERT-MK1-READY-001 | MK1 replay-build readiness | CERTIFIED | MK0 + Definition of Ready | architecture-changing dependency |
| CERT-MK1-DF-SPEC-001 | Data Foundry architecture/contracts/policies | CERTIFIED | Foundry docs/config/schema/foundation | semantic contract changes |
| CERT-MK1-DF-TOOLCHAIN-001..004 | Historical toolchains | INVALIDATED | historical evidence | superseded |
| CERT-MK1-DF-TOOLCHAIN-005 | Closure-era Foundry toolchain | CANDIDATE | role boundary + grouping + split quarantine + fresh CI/free-tier/cascade | certify only after closure semantics stabilize |
| CERT-MK1-DF-SONYC-001 | SONYC v2.3 materialization/fingerprint closure | CERTIFIED | run `34922010537`; durable `78fc0198...` | SONYC materialization/fingerprint/free-tier changes |
| EMP-MK1-CORPUS-READINESS-001 | Machine-readable corpus readiness | BLOCKED | readiness `589e7f4a...` | recomputed when input evidence/policy changes |
| EMP-DATASET-001 | Exact admitted real corpus identity/counts/durations/groups | OPEN | release-safe closure | produced only from closed corpus |
| EMP-DATA-QUALITY-001 | Duplicate/quality/diversity evidence | OPEN | dedup/group/split/coverage closure | produced only from real closure |
| CERT-MK1-DF-CORPUS-001 | Named release-safe frozen corpus | OPEN | dataset + quality + all closure gates + reproducibility + free-tier | material corpus ancestor changes |
| CERT-DOC-001..008 | Historical documentation certificates | INVALIDATED | historical audits | superseded |
| CERT-DOC-009 | Post-split documentation corpus | CERTIFIED | `DOCUMENTATION-AUDIT-2026-09-15-SPLIT-CLOSURE-009.md` | Markdown/evidence/policy/certification truth changes |
| EXT-CAMERA-001 | Real camera integration | EXTERNAL_GATE_OPEN | authorized field evidence | closes only with field evidence + upstream authorization |
| EMP-MODEL-001 | Model winner | BLOCKED | corpus cert + Benchmark A/B/C | cannot run before corpus cert |
| EMP-THRESH-001 | Event thresholds | BLOCKED | certified corpus + model/replay | cannot run before upstream gates |

## Scoped SONYC certificate

```text
CERT-MK1-DF-SONYC-001     CERTIFIED
implementation baseline  ab8c47ba6aabb25390644954a2a06945ca7a81bb
real SONYC run            34922010537
verified shards           19 / 19 PASS
probe failures            0
fingerprint failures      0
durable evidence          78fc019839f1c9dad1a58a70d439605d887361d7
```

Its scope does not certify the final corpus.

## Current empirical chain

```text
PR #11 grouping merge        8c547b70d23ce6c592ddd20d55ff37df9fa7fa03
canonical ledger evidence    9fa3d2f90ddfb731d0921749c921ab2987d54307
PR #13 split merge           03cd0627c9c6fcf0780d8d4ce48d5fa7f89fbd01
Data Foundry CI              34971457870 PASS
Free-Tier Boundary           34971457814 PASS
closure evidence run         34971457662 PASS
closure evidence             205eb419b20f10461271ff1fbbd78eb3fa9560e9
readiness run                34971547338 PASS
readiness evidence           589e7f4affed39e1ffcf6f50602d79587560bbb3
```

## Closed corpus-foundry nodes

```text
canonical fingerprint coverage    PASS / 1081 of 1081
global dedup                      PASS / gap_codes=[]
recording-family audit            PASS / gap_codes=[]
split integrity                   PASS / gap_codes=[]
```

Split policy `MK1-SPLIT-INTEGRITY-002` quarantined exactly three whole acoustic groups spanning protected source splits:

```text
ready candidate assets        1078
quarantined groups               3
quarantined assets              62
eligible development assets   1016
UNASSIGNED                       0
quarantine identity 1679540dd50eea39200f95ee98130d2e38acd0d21ca73edf7eac04040bb42aaf
```

No member was moved between protected splits. Quarantined rows remain source/ledger evidence and cannot satisfy coverage or frozen membership.

## Remaining ledger blockers

Exactly three corpus-facing rows remain non-admissible:

```text
LICENSE_NOT_RELEASE_SAFE = 1
SEMANTIC_STATUS_CONFLICT_FIRE_ALARM = 1
SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL = 1
```

They may be excluded with an auditable admission boundary or resolved by exact source evidence. They may not be coerced into corpus credit.

## Current coverage truth

`coverage-gate.json = FAIL` over 1016 development assets. It has no upstream split/dedup/group failure.

```text
FIRE_ALARM       9 assets / 6 groups / 190.182749 s
TIRE_SQUEAL     11 assets / 11 groups / 280.544098 s
GLASS_SHATTER   242 assets; FREESOUND=237, BIGSOUNDBANK=5; max source fraction=0.979339
BACKGROUND      363 assets / 362 groups / 1 source family
```

Hard-negative deficits:

```text
FIRE_ALARM       26 assets / 26 groups / 1 source
GLASS_SHATTER   342 assets / 341 groups / 1 source
SIREN            26 assets / 26 groups / 1 source
TIRE_SQUEAL       0 / 0 / 0
VEHICLE_HORN      0 / 0 / 0
```

No floor will be reduced. New credit requires genuine independent real-media evidence.

## Authoritative readiness

At `589e7f4affed39e1ffcf6f50602d79587560bbb3`:

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = c20eab44bae7cb10e7038833fdf46741d9d4c1574ebfe1b65e47dd6db160249b
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
LEDGER_LICENSE_NOT_RELEASE_SAFE_1
LEDGER_SEMANTIC_STATUS_CONFLICT_FIRE_ALARM_1
LEDGER_SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL_1
REPRODUCIBILITY_NOT_PASS
SIREN_HARD_NEGATIVE_SOURCES_1_LT_2
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
model-entry PASS
        ↓
Benchmark A/B/C authorized
```

Until then: no model training, threshold calibration, replay progression or real-camera progression.

## Dependency DAG

```text
CERT-ECHO-000 + CERT-DOC-009 + ECHO-FREE-TIER-001
        ↓
CERT-MK1-DF-SPEC-001
        ↓
TOOLCHAIN-005 CANDIDATE + SONYC-001 CERTIFIED
        ↓
FP PASS → DEDUP PASS → FAMILY PASS → SPLIT PASS
        ↓
close 3 non-admissible rows
        ↓
close real positive/background/HN/source-diversity coverage gaps
        ↓
coverage PASS → freeze #1 → freeze #2 → reproducibility PASS
        ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
        ↓
CERT-MK1-DF-CORPUS-001 → model-entry → Benchmark A/B/C
```

## Invalidation

Material changes to promise, taxonomy, source/acquisition, rights/mapping/review/probe/fingerprint, grouping/dedup, split/coverage/freeze/handoff semantics, SONYC evidence, model-entry wiring, free-tier policy, machine-readable readiness, certificate states or governing documentation require dependency review and selective recertification.
