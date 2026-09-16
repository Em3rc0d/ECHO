# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-011`

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
| CERT-MK1-DF-TOOLCHAIN-005 | Closure-era Foundry toolchain | CANDIDATE | active closure CI + deterministic evidence cascade | certify only after active closure implementation stabilizes |
| CERT-MK1-DF-SONYC-001 | SONYC v2.3 materialization/fingerprint closure | CERTIFIED | run `34922010537`; durable `78fc0198...` | SONYC evidence/materialization/fingerprint/free-tier changes |
| EMP-MK1-CORPUS-READINESS-001 | Machine-readable corpus closure readiness | BLOCKED | readiness `2088c93d...` | recomputed when input evidence/policy changes |
| EMP-DATASET-001 | Exact admitted real corpus identity/counts/durations/groups | OPEN | release-safe closure | produced only from closed corpus |
| EMP-DATA-QUALITY-001 | Duplicate/quality/diversity evidence | OPEN | dedup/group/split/coverage closure | produced only from real closure |
| CERT-MK1-DF-CORPUS-001 | Named release-safe frozen corpus | OPEN | dataset + quality + all closure gates + reproducibility + free-tier | material corpus ancestor changes |
| CERT-DOC-001..010 | Historical documentation certificates | INVALIDATED | historical audits | superseded |
| CERT-DOC-011 | Current post-Wikimedia corpus-closure documentation truth | CERTIFIED | `DOCUMENTATION-AUDIT-2026-09-15-CORPUS-CLOSURE-011.md` | audited truth changes |
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

## Current durable corpus evidence

At `main@2088c93d65b5d4dff58bb5cdb91b0e76e6288afb`:

```text
canonical ledger baseline              0e05b9ce7ef9afdbd6d0d327922f9811fa0a50d7
canonical ledger entries               1162
canonical fingerprints                 1162 / 1162
missing fingerprints                   0
unresolved ledger blockers             0
ledger sha256                          b250b18e8ccef3776cdc38d42f240a057bcf99b260cc6cb58a77aad93e9d0cab
fallback assets after grouping         0
global acoustic components             14
members reassigned to components       125
content merge/delete                   false
```

Closed structural gates:

```text
global-dedup-audit.json       PASS / gap_codes=[]
recording-family-audit.json   PASS / gap_codes=[]
split-integrity.json          PASS / gap_codes=[]
protected split conflicts     2
quarantined assets            93
```

## Current final coverage truth

```text
BACKGROUND
  416 assets / 383 groups / 4 sources                   PASS

FIRE_ALARM
  12 assets / 9 groups / 311.05767 s / 3 sources
  BIGSOUNDBANK 4 / FREESOUND 5 / WIKIMEDIA_COMMONS 3
  train 10/7, validation 2/2, test 0/0
  HN 206 assets / 206 groups / 4 sources                 PASS

GLASS_SHATTER
  239 assets / 222 groups
  BIGSOUNDBANK 6 / FREESOUND 226
  OPENGAMEART_RUBBERDUCK 6 / OPENGAMEART_TILL_BEHREND 1
  max single-source fraction 0.945607                    FAIL <= 0.80
  HN 428 assets / 408 groups / 2 sources                 PASS

SIREN
  173 assets / 173 groups
  HN 245 assets / 244 groups / 4 sources                 PASS

TIRE_SQUEAL
  11 assets / 11 groups / 280.544098 s
  train 9/9, validation 0/0, test 2/2
  HN 25 assets / 12 groups / 2 sources                   PASS

VEHICLE_HORN
  245 assets / 244 groups
  HN 146 assets / 146 groups / 3 sources                 PASS
```

Coverage is `FAIL` with exactly 17 detailed gap codes: eight FIRE positive/split gaps, one GLASS concentration gap and eight TIRE positive/split gaps. Asset-quality stop lines remain zero.

## Machine-readable readiness

At `2088c93d65b5d4dff58bb5cdb91b0e76e6288afb`:

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = 9b6da43da378dbf546a3961c6ed47b8e7218b5135bbe84680f58eecf86030559
```

Exact readiness gaps:

```text
CORPUS_CERTIFICATE_NOT_CERTIFIED
COVERAGE_GATE_GAP_CODES_NOT_EMPTY
COVERAGE_GATE_NOT_PASS
COVERAGE_GATE_STATUS_NOT_PASS
FIRE_ALARM_ASSETS_12_LT_50
FREEZE_1_VALIDATION_NOT_PASS
FREEZE_2_VALIDATION_NOT_PASS
REPRODUCIBILITY_NOT_PASS
TIRE_SQUEAL_ASSETS_11_LT_50
```

## Freesound evidence boundary

The next FIRE/TIRE acquisition is not pre-certified. Freesound generated reports must be SHA-bound and rejected if `main` moves. Raw supplemental semantic configuration must not race Canonical Ledger before fresh materialization evidence exists. Candidate rows receive zero empirical corpus credit until they survive materialization → canonical ledger → grouping/dedup → split → coverage → readiness.

## Product critical path

```text
CERT-ECHO-000 + CERT-DOC-011 + ECHO-FREE-TIER-001
        ↓
CERT-MK1-DF-SPEC-001
        ↓
TOOLCHAIN-005 = CANDIDATE + SONYC-001 = CERTIFIED
        ↓
GLOBAL DEDUP + RECORDING FAMILY + SPLIT INTEGRITY = PASS
        ↓
real coverage / source-diversity acquisition
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
