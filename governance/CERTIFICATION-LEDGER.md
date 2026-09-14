# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-005`

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
| CERT-MK1-DF-TOOLCHAIN-001 | Historical 42-test toolchain | INVALIDATED | old baseline `2c4d4c2...` | superseded |
| CERT-MK1-DF-TOOLCHAIN-002 | Historical 67-test toolchain | INVALIDATED | baseline `be75a432...`, run `34800084225` | superseded by readiness/guard changes |
| CERT-MK1-DF-TOOLCHAIN-003 | Current Foundry toolchain + fail-closed readiness/model-entry guard | CERTIFIED | baseline `dc225803...`, Data Foundry CI `34904125873`, readiness run `34904125899`, free-tier run `34904125820` | governed Foundry/readiness/guard surface changes |
| EMP-MK1-CORPUS-READINESS-001 | Machine-readable corpus closure readiness | BLOCKED | durable `corpus-closure-readiness.json` at `aac662b...` | recomputed whenever input evidence/policy changes |
| EMP-DATASET-001 | Exact admitted real corpus identity/counts/durations/groups | OPEN | real release-safe closure | produced only from closed corpus |
| EMP-DATA-QUALITY-001 | Duplicate/quality/diversity evidence | OPEN | global dedup/group/split/coverage evidence | produced only from real closure |
| CERT-MK1-DF-CORPUS-001 | Named release-safe frozen corpus | OPEN | EMP-DATASET-001 + EMP-DATA-QUALITY-001 + all DF closure gates + reproducibility + free-tier PASS | any source/asset/policy/mapping/group/split/fingerprint/freeze change |
| CERT-DOC-001 | Historical initial documentation audit | INVALIDATED | historical corpus | superseded |
| CERT-DOC-002 | Historical Foundry documentation audit | INVALIDATED | historical corpus | superseded |
| CERT-DOC-003 | Historical 197-file corpus | INVALIDATED | commit `7ef9c1d...` | superseded |
| CERT-DOC-004 | Historical 206-file Corpus Closure baseline | INVALIDATED | 2026-09-13 audit | superseded by readiness/toolchain delta |
| CERT-DOC-005 | Current 208-file documentation corpus | CERTIFIED | `DOCUMENTATION-AUDIT-2026-09-14-CORPUS-READINESS.md` | Markdown/policy truth changes without audit |
| EXT-CAMERA-001 | Real camera integration | EXTERNAL_GATE_OPEN | authorized camera/site evidence | closes only with field evidence and upstream authorization |
| EMP-MODEL-001 | Model winner | BLOCKED | certified corpus + Benchmark A/B/C | cannot run before corpus cert |
| EMP-THRESH-001 | Classifier/Event Engine thresholds | BLOCKED | certified corpus + validation/replay | cannot run before corpus/model gates |
| EMP-DIST-001 | Distance/SNR envelope | BLOCKED | authorized field tests | external + upstream gates |
| EMP-CAP-001 | Multi-source capacity envelope | OPEN | future runtime load/soak | runtime evidence changes |
| EMP-SLO-001 | Final MK1/MK2 SLO evidence | OPEN | runtime/quality/field evidence | evidence changes |

## Current Data Foundry recertification

`CERT-MK1-DF-TOOLCHAIN-003` supersedes toolchain-002 because code governed by the Foundry certificate changed materially. The new certificate adds deterministic closure-readiness computation and a reusable model-entry guard.

Exact evidence:

```text
implementation baseline   dc225803b5c066b365779fdc2b4b2f0984bb7e19
Data Foundry CI            34904125873  PASS on Python 3.10 / 3.11 / 3.12
Free-Tier Boundary         34904125820  PASS
Corpus Closure Readiness   34904125899  PASS as deterministic evidence generation
durable readiness commit   aac662b770669bf633dd58a582514abcb39c30a1
```

The readiness result being `BLOCKED` is not a CI failure. It is the correct empirical state: evidence generation itself is valid, while downstream model authorization remains false.

## Corpus readiness truth

The current readiness artifact states:

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
modeling_allowed              = false
eligible_for_certificate_review = false
CERT-MK1-DF-CORPUS-001       = OPEN
next_authorized_stage         = CORPUS_FOUNDRY_CLOSURE
```

Important current gaps include:

```text
FIRE_ALARM_ASSETS_5_LT_50
TIRE_SQUEAL_ASSETS_5_LT_50
TIRE_SQUEAL_UNDERLYING_SOURCES_1_LT_2
VEHICLE_HORN_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
FIRE_ALARM_HARD_NEGATIVE_SOURCES_1_LT_2
GLASS_SHATTER_HARD_NEGATIVE_SOURCES_1_LT_2
SIREN_HARD_NEGATIVE_SOURCES_1_LT_2
CANONICAL_FINGERPRINT_COVERAGE_INCOMPLETE
```

The final global-dedup, recording-family, split-integrity, coverage, two freeze-validation and reproducibility artifacts also remain unpassed/missing.

## Release law

The following dependency is mandatory and executable:

```text
CERT-MK1-DF-CORPUS-001 = CERTIFIED
AND gap_codes=[]
AND reproducibility PASS
AND ECHO-FREE-TIER-001 PASS
        ↓
model-entry gate PASS
        ↓
Benchmark A/B/C authorized
```

Without it:

```text
NO Benchmark A/B/C
NO YAMNet/PANNs/CNN model work
NO EMP-MODEL-001
NO threshold calibration
NO replay pipeline
NO real-camera progression
```

No floor reduction, broad-label coercion, synthetic source inflation, duplicate-family inflation or paid infrastructure is an accepted route around this law.

## Documentation lineage

```text
CERT-DOC-001  historical / invalidated
CERT-DOC-002  historical / invalidated
CERT-DOC-003  historical / invalidated
CERT-DOC-004  historical / invalidated by readiness/toolchain delta
CERT-DOC-005  current / CERTIFIED / 208 Markdown files
```

`CERT-DOC-005` synchronizes current state, Foundry gates, toolchain recertification 003, machine-readable readiness and this ledger. It does not close any empirical gap.

## Dependency DAG

```text
CERT-ECHO-000
  + CERT-DOC-005
  + ECHO-FREE-TIER-001
          ↓
CERT-MK0-013
          ↓
CERT-MK1-READY-001
          ↓
CERT-MK1-DF-SPEC-001
          ↓
CERT-MK1-DF-TOOLCHAIN-003
          ↓
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
          ↓
close corpus gaps + global audits + split + coverage + freeze×2
          ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
          ↓
CERT-MK1-DF-CORPUS-001
          ↓
model-entry gate
          ↓
Benchmark A/B/C
          ↓
EMP-MODEL-001
          ↓
EMP-THRESH-001
```

`EXT-CAMERA-001` remains external and cannot authorize field progression before the corpus/model chain permits it.

## Invalidation

A material change to promise, taxonomy, schema, source/audio/event contract, source/acquisition registry, rights/mapping/review/probe/fingerprint/coverage/dedup/group/split/manifest/freeze/handoff semantics, model-entry guard, benchmark set, delivery/privacy policy, zero-cost execution boundary or governing documentation requires dependency review and selective invalidation/re-certification.

Git history + content hashes + manifests + CI evidence are the traceability mechanism; ECHO does not claim blockchain consensus.
