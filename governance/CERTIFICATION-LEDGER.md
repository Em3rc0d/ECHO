# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-012`

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
| EMP-MK1-CORPUS-READINESS-001 | Machine-readable corpus closure readiness | BLOCKED | readiness `48af9f22...` | recomputed when input evidence/policy changes |
| EMP-DATASET-001 | Exact admitted real corpus identity/counts/durations/groups | OPEN | release-safe closure | produced only from closed corpus |
| EMP-DATA-QUALITY-001 | Duplicate/quality/diversity evidence | OPEN | dedup/group/split/coverage closure | produced only from real closure |
| CERT-MK1-DF-CORPUS-001 | Named release-safe frozen corpus | OPEN | dataset + quality + all closure gates + reproducibility + free-tier | material corpus ancestor changes |
| CERT-DOC-001..011 | Historical documentation certificates | INVALIDATED | historical audits | superseded |
| CERT-DOC-012 | Current post-Freesound-rematerialization closure truth | CERTIFIED | `DOCUMENTATION-AUDIT-2026-09-16-CORPUS-CLOSURE-012.md` | audited truth changes |
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

At `main@48af9f220b30f2197aa376bff025195cb0a2a13b`:

```text
canonical ledger baseline              050f2ebc39fea0d1e6903190ad471fd97d1487dc
canonical ledger entries               1141
canonical fingerprints                 1141 / 1141
missing fingerprints                   0
unresolved ledger blockers             0
ledger sha256                          1ab3712452f42205fe9004f1d6cb9e778297487891bb373e5c42d635854f1d85
fallback assets after grouping         0
global acoustic components             12
members reassigned to components       118
content merge/delete                   false
```

The live release-safe Freesound rebuild reduced the ledger from the DOC-011 snapshot. This is accepted current evidence, not an operator deletion to improve metrics.

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
  19 assets / 16 groups / 460.864037 s / 3 sources
  BIGSOUNDBANK 4 / FREESOUND 12 / WIKIMEDIA_COMMONS 3
  train 17/14, validation 2/2, test 0/0
  HN 202 assets / 202 groups / 4 sources                 PASS

GLASS_SHATTER
  222 assets / 205 groups
  BIGSOUNDBANK 6 / FREESOUND 209
  OPENGAMEART_RUBBERDUCK 6 / OPENGAMEART_TILL_BEHREND 1
  max single-source fraction 0.941441                    FAIL <= 0.80
  HN 428 assets / 408 groups / 2 sources                 PASS

SIREN
  169 assets / 169 groups
  HN 235 assets / 235 groups / 4 sources                 PASS

TIRE_SQUEAL
  14 assets / 10 groups / 344.600098 s / 2 sources
  BIGSOUNDBANK 5 / FREESOUND 9
  train 11/8, validation 0/0, test 3/2
  HN 25 assets / 12 groups / 2 sources                   PASS

VEHICLE_HORN
  235 assets / 235 groups
  HN 142 assets / 142 groups / 3 sources                 PASS
```

Coverage is `FAIL` with exactly 16 detailed gap codes: seven FIRE positive/split gaps, one GLASS concentration gap and eight TIRE positive/split gaps. `FIRE_ALARM_TRAIN_GROUPS_BELOW_MIN` is closed. Asset-quality stop lines remain zero.

## Machine-readable readiness

At `48af9f220b30f2197aa376bff025195cb0a2a13b`:

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = 85dee5596dbc9c88e0430e32b5e8eec7c014d526d132974542b2e4a36a108a50
```

Exact readiness gaps:

```text
CORPUS_CERTIFICATE_NOT_CERTIFIED
COVERAGE_GATE_GAP_CODES_NOT_EMPTY
COVERAGE_GATE_NOT_PASS
COVERAGE_GATE_STATUS_NOT_PASS
FIRE_ALARM_ASSETS_19_LT_50
FREEZE_1_VALIDATION_NOT_PASS
FREEZE_2_VALIDATION_NOT_PASS
REPRODUCIBILITY_NOT_PASS
TIRE_SQUEAL_ASSETS_14_LT_50
```

## Evidence-only acquisition boundary

A public source may be scouted and materialized before corpus admission only if the lane is explicitly evidence-only. Such a lane may verify rights/provenance, fetch bytes, probe and fingerprint them, but it must not be connected to Canonical Ledger or receive source-diversity/coverage credit until a later reviewed admission change.

Hosting/wrapper identity is not acoustic-origin identity. Derivatives and mirrors inherit the underlying acoustic source family unless independent recording provenance is proven.

## Product critical path

```text
CERT-ECHO-000 + CERT-DOC-012 + ECHO-FREE-TIER-001
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
