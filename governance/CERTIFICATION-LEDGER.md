# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-009`

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
| CERT-MK1-DF-TOOLCHAIN-005 | Closure-era Foundry toolchain | CANDIDATE | PR #10-#15 + fresh CI/cascade | certify only after active closure implementation stabilizes |
| CERT-MK1-DF-SONYC-001 | SONYC v2.3 materialization/fingerprint closure | CERTIFIED | run `34922010537`; durable `78fc0198...` | SONYC evidence/materialization/fingerprint/free-tier changes |
| EMP-MK1-CORPUS-READINESS-001 | Machine-readable corpus closure readiness | BLOCKED | readiness `d94eff29...` | recomputed when input evidence/policy changes |
| EMP-DATASET-001 | Exact admitted real corpus identity/counts/durations/groups | OPEN | release-safe closure | produced only from closed corpus |
| EMP-DATA-QUALITY-001 | Duplicate/quality/diversity evidence | OPEN | dedup/group/split/coverage closure | produced only from real closure |
| CERT-MK1-DF-CORPUS-001 | Named release-safe frozen corpus | OPEN | dataset + quality + all closure gates + reproducibility + free-tier | material corpus ancestor changes |
| CERT-DOC-001..008 | Historical documentation certificates | INVALIDATED | historical audits | superseded |
| CERT-DOC-009 | Current corpus-closure documentation truth | CERTIFIED | `DOCUMENTATION-AUDIT-2026-09-15-CORPUS-CLOSURE-009.md` | audited truth changes |
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

## Current empirical chain

```text
PR #15 merge / implementation baseline  4b261bd10d6578a6256fca8ec848ea1055c24b32
Data Foundry CI                          34980804090 PASS
canonical ledger run                     34980804004 PASS
canonical ledger durable evidence        5239447e91915deef30b814c6b172010bd73d2ff
closure evidence run                     34980883811 PASS
closure evidence durable commit          b4086d7eb02df67091ac77cd519590abf336b70e
readiness durable commit                 d94eff2958bbe57076610524cbb192d14ec95739
```

## Canonical corpus-facing ledger

```text
entry_count                         1078
canonical fingerprints              1078 / 1078
missing fingerprints                   0
unresolved ledger blockers             0
fallback assets after grouping          0
global acoustic components             17
assets moved into acoustic components  97
content merge/delete                false
ledger sha256                        36ef8e19198a296d7806106adc2c4ee43b7827d893e78b6bbd2d1ffd83b3743a
```

The former non-release-safe/semantic-conflict rows are quarantined from corpus credit without altering their source evidence.

## Closed structural gates

```text
global-dedup-audit.json       PASS / gap_codes=[]
recording-family-audit.json   PASS / gap_codes=[]
split-integrity.json          PASS / gap_codes=[]
```

Split PASS is achieved by deterministic whole-group quarantine for the three incompatible protected upstream split components. The 62 quarantined assets cannot satisfy coverage/freeze membership and are not remapped individually.

## Current coverage/readiness truth

Current target precheck:

```text
FIRE_ALARM      positive 9/50     HN 34/20    HN sources 1/2
GLASS_SHATTER   positive 304/50   HN 401/20   HN sources 1/2
SIREN           positive 173/50   HN 32/20    HN sources 1/2
TIRE_SQUEAL     positive 11/50    HN 0/20     HN sources 0/2
VEHICLE_HORN    positive 245/50   HN 0/20     HN sources 0/2
```

Coverage remains FAIL because these prechecks are only a subset of the full solidity law; groups, duration, splits, concentration, quality and rights remain enforced. Floors may not be reduced.

At `d94eff2958bbe57076610524cbb192d14ec95739`:

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = 90f2dd006cfbacfe9dc1bdc5cb81c7d9411ccf5322d6ca2dd53f334e76c209e8
```

Exact readiness gap codes:

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

## Product critical path

```text
CERT-ECHO-000 + CERT-DOC-009 + ECHO-FREE-TIER-001
        ↓
CERT-MK1-DF-SPEC-001
        ↓
TOOLCHAIN-005 = CANDIDATE + SONYC-001 = CERTIFIED
        ↓
GLOBAL DEDUP + RECORDING FAMILY + SPLIT INTEGRITY = PASS
        ↓
real coverage / source-diversity / HN acquisition
        ↓
coverage PASS → freeze #1 → freeze #2 → reproducibility PASS
        ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
        ↓
CERT-MK1-DF-CORPUS-001
        ↓
model-entry → Benchmark A/B/C
        ↓
model winner → Event Engine → Edge Agent → MQTT/replay → real camera
```

Supporting infrastructure cannot preempt this sequence or redefine ECHO as a camera/dashboard/integration project.

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

## Invalidation

Material changes to promise, taxonomy, source/acquisition, rights/mapping/review/probe/fingerprint, grouping/dedup, split/coverage/freeze/handoff semantics, SONYC evidence, model-entry wiring, free-tier policy, machine-readable readiness, certificate states or governing documentation require dependency review and selective recertification.