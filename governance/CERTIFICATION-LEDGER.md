# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-014`

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
| CERT-MK1-DF-TOOLCHAIN-005 | Atomic closure-era Foundry toolchain | CANDIDATE | active CI + deterministic atomic evidence cascade | certify after active closure/certificate implementation stabilizes |
| CERT-MK1-DF-SONYC-001 | SONYC v2.3 materialization/fingerprint closure | CERTIFIED | run `34922010537`; durable `78fc0198...` | SONYC evidence/materialization/fingerprint/free-tier changes |
| EMP-MK1-CORPUS-READINESS-001 | Machine-readable corpus closure readiness v2 | BLOCKED | semantic ledger + policy + closure evidence | recomputed when semantic evidence/policy changes |
| EMP-DATASET-001 | Exact admitted real corpus identity/counts/durations/groups | OPEN | release-safe closure | produced only from closed corpus |
| EMP-DATA-QUALITY-001 | Duplicate/quality/diversity evidence | OPEN | dedup/group/split/coverage closure | produced only from real closure |
| CERT-MK1-DF-CORPUS-001 | Named release-safe frozen corpus | OPEN | dataset + quality + all closure gates + reproducibility + free-tier | material corpus ancestor changes |
| CERT-DOC-001..013 | Historical documentation certificates | INVALIDATED | historical audits | superseded |
| CERT-DOC-014 | Current atomic-pipeline + semantic-identity truth | CERTIFIED | `DOCUMENTATION-AUDIT-2026-09-16-CORPUS-PIPELINE-014.md` | audited semantic truth changes |
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

## Corpus identity boundary

The canonical semantic corpus identity is:

```text
ledger semantic sha256    cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1
coverage material sha256  93be3dceee44df0dfc51ab38c078f1e1e6587ba91e4fbbc53c3b65065e58bfa8
readiness-v2 identity     4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
```

`baseline_commit` and raw generated-summary hashes are execution provenance. They remain mandatory and auditable, but they do not redefine the acoustic corpus when semantic ledger/policy/closure identities remain unchanged.

## Atomic durable corpus evidence

The active TOOLCHAIN-005 candidate uses one durable writer:

```text
governed source materialization
  ↓
atomic corpus orchestrator
  ↓
canonical ledger → grouping → dedup/family/split → coverage
  ↓
freeze #1 → freeze #2 → reproducibility → readiness v2
  ↓
one durable evidence commit
```

The full cascade is repeated and byte-compared for determinism. Persistence is refused if the exact execution baseline no longer equals `origin/main`. Closure/readiness standalone workflows are diagnostics only and cannot write to `main`.

Current semantic ledger truth:

```text
canonical ledger entries               1141
canonical fingerprints                 1141 / 1141
missing fingerprints                   0
unresolved ledger blockers             0
fallback assets after grouping         0
global acoustic components             2
members reassigned to components       4
content merge/delete                   false
```

## Near-duplicate and split closure

```text
candidate threshold                    0.02
confirmed threshold                   0.002
max decoded-sample delta               0.01
candidate relations                    855
candidate cross-group                  849
confirmed relations                    2
confirmed cross-group conflicts        0
length-rejected candidates             835

global-dedup-audit.json       PASS / gap_codes=[]
recording-family-audit.json   PASS / gap_codes=[]
split-integrity.json          PASS / gap_codes=[]
protected split conflicts     0
quarantined assets            0
development assets            1141
```

Broad RMS-envelope proximity is screening only. Review-only edges do not form transitive recording identity. Exact byte/PCM identity and strict confirmed relations remain split-protection evidence.

## Current final coverage truth

```text
BACKGROUND
  428 assets / 385 groups / 4 sources                   PASS

FIRE_ALARM
  19 assets / 16 groups / 460.864037 s / 3 sources
  BIGSOUNDBANK 4 / FREESOUND 12 / WIKIMEDIA_COMMONS 3
  train 17/14, validation 2/2, test 0/0
  HN 202 assets / 202 groups / 4 sources                PASS

GLASS_SHATTER
  303 assets / 287 groups / 1244.131193 s
  BIGSOUNDBANK 16 / FREESOUND 280
  OPENGAMEART_RUBBERDUCK 6 / OPENGAMEART_TILL_BEHREND 1
  max single-source fraction 0.924092                   FAIL <= 0.80
  HN 440 assets / 410 groups / 2 sources                PASS

SIREN
  169 assets / 169 groups
  HN 235 assets / 235 groups / 4 sources                PASS

TIRE_SQUEAL
  14 assets / 10 groups / 344.600098 s / 2 sources
  BIGSOUNDBANK 5 / FREESOUND 9
  train 11/8, validation 0/0, test 3/2
  HN 25 assets / 12 groups / 2 sources                  PASS

VEHICLE_HORN
  235 assets / 235 groups
  HN 142 assets / 142 groups / 3 sources                PASS
```

Coverage is `FAIL` with exactly 16 empirical gap codes: seven FIRE positive/split gaps, one GLASS concentration gap and eight TIRE positive/split gaps. Asset-quality stop lines remain zero.

## Current empirical lower bounds

```text
FIRE_ALARM   +31 assets, +9 groups minimum
TIRE_SQUEAL  +36 assets, +15 groups minimum
GLASS        +47 surviving non-Freesound positives minimum if Freesound remains 280
```

These are mathematical/evidence lower bounds. They do not authorize manual split placement, source-family inflation or bypass of rights/dedup/grouping gates.

## Machine-readable readiness

```text
schema = echo.corpus-closure-readiness.v2
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
semantic evidence identity = 4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
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

Freeze #1 and #2 are blocked only by coverage. Reproducibility is blocked only because freeze is not eligible.

## Evidence-only acquisition boundary

A public source may be scouted and materialized before corpus admission only if the lane is explicitly evidence-only. Such a lane may verify rights/provenance, fetch bytes, probe and fingerprint them, but it must not be connected to Canonical Ledger or receive source-diversity/coverage credit until a later reviewed admission change.

Hosting/wrapper identity is not acoustic-origin identity. Derivatives and mirrors inherit the underlying acoustic source family unless independent recording provenance is proven.

## Product critical path

```text
CERT-ECHO-000 + CERT-DOC-014 + ECHO-FREE-TIER-001
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

Material changes to promise, taxonomy, source/acquisition, rights/mapping/review/probe/fingerprint, grouping/dedup, split/coverage/freeze/handoff semantics, semantic corpus identity, SONYC evidence, model-entry wiring, free-tier policy, readiness identity contract, certificate states or governing documentation require dependency review and selective recertification.

A pure execution provenance change does not by itself redefine the corpus when all semantic identities remain identical, but provenance must remain valid and internally consistent.
