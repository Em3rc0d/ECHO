# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-008`

`CERTIFIED` is always scope-bounded. Green CI is execution evidence, not a substitute for missing empirical corpus evidence. No certificate may depend on a path that violates `ECHO-FREE-TIER-001`.

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
| CERT-MK1-DF-TOOLCHAIN-004 | SONYC persistence/fingerprint Foundry baseline | INVALIDATED | baseline `ab8c47ba...` | invalidated by closure semantic changes |
| CERT-MK1-DF-TOOLCHAIN-005 | Closure-era Foundry toolchain | CANDIDATE | PR #10/#11 + fresh CI/free-tier/cascade | certify only after active closure implementation stabilizes |
| CERT-MK1-DF-SONYC-001 | SONYC v2.3 materialization/fingerprint closure | CERTIFIED | run `34922010537`; durable `78fc0198...` | SONYC evidence/materialization/fingerprint/free-tier changes |
| EMP-MK1-CORPUS-READINESS-001 | Machine-readable corpus closure readiness | BLOCKED | readiness `8e7702a2...` | recomputed when input evidence/policy changes |
| EMP-DATASET-001 | Exact admitted real corpus identity/counts/durations/groups | OPEN | release-safe closure | produced only from closed corpus |
| EMP-DATA-QUALITY-001 | Duplicate/quality/diversity evidence | OPEN | dedup/group/split/coverage closure | produced only from real closure |
| CERT-MK1-DF-CORPUS-001 | Named release-safe frozen corpus | OPEN | dataset + quality + all closure gates + reproducibility + free-tier | material corpus ancestor changes |
| CERT-DOC-001..006 | Historical documentation certificates | INVALIDATED | historical audits | superseded |
| CERT-DOC-007 | Corpus-role-boundary documentation audit | INVALIDATED | 211-file audit | superseded by fresh grouping cascade |
| CERT-DOC-008 | Post-grouping documentation corpus | CERTIFIED | `DOCUMENTATION-AUDIT-2026-09-15-GROUPING-CLOSURE-008.md` | Markdown/evidence/policy/certification truth changes |
| EXT-CAMERA-001 | Real camera integration | EXTERNAL_GATE_OPEN | authorized field evidence | closes only with field evidence + upstream authorization |
| EMP-MODEL-001 | Model winner | BLOCKED | corpus cert + Benchmark A/B/C | cannot run before corpus cert |
| EMP-THRESH-001 | Event thresholds | BLOCKED | certified corpus + model/replay | cannot run before upstream gates |

## SONYC scoped certificate

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

## Post-grouping empirical chain

```text
PR #11 merge                 8c547b70d23ce6c592ddd20d55ff37df9fa7fa03
Data Foundry CI              34969860336 PASS
Documentation Governance     34969860448 PASS
Free-Tier Boundary           34969860642 PASS
canonical ledger run         34969860666 PASS
canonical ledger evidence    9fa3d2f90ddfb731d0921749c921ab2987d54307
closure evidence run         34969945975 PASS
closure evidence             e3e0f58dee3a1602e92f62c8a7708fa1e9fad9ea
readiness run                34970028139 PASS
readiness evidence           8e7702a2bf629642f78859763dabbe09df03df02
```

Canonical corpus-facing ledger:

```text
entry_count                         1081
canonical fingerprints              1081 / 1081
fallback assets before grouping      448
fallback assets after grouping         0
global acoustic components            17
screened fallback groups              357
assets moved into acoustic components  97
```

Global closure nodes now empirically PASS:

```text
global-dedup-audit.json       PASS / gap_codes=[]
recording-family-audit.json   PASS / gap_codes=[]
```

The three remaining ledger blockers are exact:

```text
LICENSE_NOT_RELEASE_SAFE = 1
SEMANTIC_STATUS_CONFLICT_FIRE_ALARM = 1
SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL = 1
```

## Current split and coverage truth

`split-integrity.json = FAIL` because three global acoustic components span recognized upstream split assignments. 62 otherwise-ready assets are currently unassigned. Any fix must preserve whole acoustic groups; manual clip movement and seed shopping are forbidden.

Current final coverage exposes real deficits, including:

```text
FIRE_ALARM       9 assets / 6 groups
TIRE_SQUEAL     11 assets / 11 groups
GLASS_SHATTER   largest source fraction 0.976974 > 0.80
BACKGROUND      1 source family < 3

HN source families:
FIRE_ALARM       1 < 2
GLASS_SHATTER    1 < 2
SIREN            1 < 2
TIRE_SQUEAL      0 < 2; 0 assets < 20
VEHICLE_HORN     0 < 2; 0 assets < 20
```

These are not candidates for floor reduction. They require source-safe exclusion where invalid and genuine real-media acquisition where coverage is insufficient.

## Authoritative readiness

At `8e7702a2bf629642f78859763dabbe09df03df02`:

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = fcd07c11d3291d5a78ee28cae93e42de0f16e78522720e78fffb5e71b4bcf129
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
AND all required closure evidence = PASS
AND reproducibility = PASS
AND ECHO-FREE-TIER-001 = PASS
        ↓
model-entry PASS
        ↓
Benchmark A/B/C authorized
```

Until then there is no model training, threshold calibration, replay progression or real-camera progression.

## Dependency DAG

```text
CERT-ECHO-000 + CERT-DOC-008 + ECHO-FREE-TIER-001
        ↓
CERT-MK1-DF-SPEC-001
        ↓
TOOLCHAIN-005 = CANDIDATE + SONYC-001 = CERTIFIED
        ↓
GLOBAL DEDUP = PASS + RECORDING FAMILY = PASS
        ↓
close 3 row blockers + protected-split conflicts
        ↓
close real coverage / source-diversity / HN gaps
        ↓
coverage PASS → freeze #1 → freeze #2 → reproducibility PASS
        ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
        ↓
CERT-MK1-DF-CORPUS-001
        ↓
model-entry → Benchmark A/B/C
```

## Invalidation

Material changes to promise, taxonomy, source/acquisition, rights/mapping/review/probe/fingerprint, grouping/dedup, split/coverage/freeze/handoff semantics, SONYC evidence, model-entry wiring, free-tier policy, machine-readable readiness, certificate states or governing documentation require dependency review and selective recertification.
