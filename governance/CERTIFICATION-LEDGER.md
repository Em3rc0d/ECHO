# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-015`

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
| CERT-MK1-DF-TOOLCHAIN-004 | SONYC persistence/fingerprint Foundry baseline | INVALIDATED | historical closure baseline | superseded by closure semantics |
| CERT-MK1-DF-TOOLCHAIN-005 | Atomic closure-era Foundry toolchain through readiness v2 | CERTIFIED | PR #43/#47/#48; run `35159518112`; durable `40b1fb44...` | certified Foundry semantics/wiring/free-tier change |
| CERT-MK1-DF-SONYC-001 | SONYC v2.3 materialization/fingerprint closure | CERTIFIED | run `34922010537`; durable `78fc0198...` | SONYC evidence/materialization/fingerprint/free-tier changes |
| CERT-MK1-DF-HANDOFF-001 | Corpus certificate transition authority | CERTIFIED | `MK1/build/data-foundry/CORPUS-CERTIFICATE-HANDOFF.md` + current tests/wiring | certificate transition semantics change |
| EMP-MK1-CORPUS-READINESS-001 | Machine-readable corpus closure readiness v2 | BLOCKED | semantic ledger + policy + closure evidence | recomputed when semantic evidence/policy changes |
| EMP-DATASET-001 | Exact admitted real corpus identity/counts/durations/groups | OPEN | release-safe closure | produced only from closed corpus |
| EMP-DATA-QUALITY-001 | Duplicate/quality/diversity evidence | OPEN | dedup/group/split/coverage closure | produced only from real closure |
| CERT-MK1-DF-CORPUS-001 | Named release-safe frozen corpus | OPEN | dataset + quality + all closure gates + reproducibility + handoff + free-tier | semantic corpus/ancestor changes |
| CERT-DOC-001..014 | Historical documentation certificates | INVALIDATED | historical audits | superseded |
| CERT-DOC-015 | Current corpus-certificate-handoff truth | CERTIFIED | `DOCUMENTATION-AUDIT-2026-09-16-CORPUS-HANDOFF-015.md` | audited truth changes |
| EXT-CAMERA-001 | Real camera integration | EXTERNAL_GATE_OPEN | authorized field evidence | closes only with field evidence + upstream authorization |
| EMP-MODEL-001 | Model winner | BLOCKED | corpus cert + Benchmark A/B/C | cannot run before corpus cert |
| EMP-THRESH-001 | Event thresholds | BLOCKED | certified corpus + model/replay | cannot run before upstream gates |

## Certified Toolchain-005 evidence

```text
implementation merge             7cabdceecec9389153af4335e5e3b4564259776b
atomic workflow run              35159518112
atomic durable evidence commit   40b1fb44921dfa98cf4fba03e652c1b0fa5abd2f
```

Toolchain-005 certifies deterministic release-safe corpus construction through atomic closure and readiness v2. It does not certify current corpus sufficiency and does not itself issue the corpus certificate.

## Corpus identity boundary

```text
canonical assets             1141
canonical fingerprints       1141 / 1141
semantic ledger sha256       cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1
coverage material sha256     93be3dceee44df0dfc51ab38c078f1e1e6587ba91e4fbbc53c3b65065e58bfa8
readiness-v2 identity        4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
ledger blockers              0
split quarantine             0
```

`baseline_commit` and raw generated-summary hashes are execution provenance. They remain mandatory and auditable, but they do not redefine the acoustic corpus when semantic ledger/policy/closure identities remain unchanged.

## Structural closure

```text
global dedup             PASS / gap_codes=[]
recording-family audit   PASS / gap_codes=[]
split integrity          PASS / gap_codes=[]
confirmed near-duplicate cross-group conflicts 0
exact duplicate groups   0
```

The active near-duplicate policy is `screen -> confirm -> group`. Broad RMS-envelope proximity is screening only; review-only edges do not create transitive recording identity.

## Current empirical coverage

Coverage is `FAIL` with exactly 16 empirical gaps:

```text
FIRE_ALARM
  19 assets / 16 groups / 3 sources
  train 17/14, validation 2/2, test 0/0
  minimum lower bound: +31 assets / +9 groups

GLASS_SHATTER
  303 assets / 287 groups / 4 sources
  Freesound 280 / total 303 / fraction 0.924092
  minimum lower bound: +47 surviving non-Freesound positives if Freesound remains 280

TIRE_SQUEAL
  14 assets / 10 groups / 2 sources
  train 11/8, validation 0/0, test 3/2
  minimum lower bound: +36 assets / +15 groups
```

BACKGROUND and all current hard-negative floors remain PASS. Asset-quality stop lines remain zero. These lower bounds do not authorize manual split placement, source-family inflation or quality-floor reduction.

## Handoff authority

`CERT-MK1-DF-HANDOFF-001` freezes the only authorized automatic transition:

```text
coverage PASS / gap_codes=[]
→ freeze #1 PASS
→ freeze #2 clean PASS
→ reproducibility PASS
→ pre-certificate readiness
→ gap_codes == [CORPUS_CERTIFICATE_NOT_CERTIFIED]
→ CERT-MK1-DF-CORPUS-001
→ final readiness READY / gap_codes=[] / modeling_allowed=true
→ Benchmark A/B/C
```

If any additional gap remains, certificate issuance is a no-op and model entry stays locked. A valid certificate is bound to the semantic readiness identity plus SHA-pinned Toolchain-005, Handoff-001 and Free-Tier authorities.

## Current readiness

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
schema_version = echo.corpus-closure-readiness.v2
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = 4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
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

Material changes to promise, taxonomy, source/acquisition, rights/mapping/review/probe/fingerprint, grouping/dedup, split/coverage/freeze/handoff semantics, Toolchain-005, SONYC evidence, model-entry wiring, Free Tier, machine-readable readiness, certificate states or governing documentation require dependency review and selective recertification.