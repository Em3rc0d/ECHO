# ECHO Documentation Audit — Corpus Closure 013

**Certificate:** `CERT-DOC-013`  
**Status:** `CERTIFIED`  
**Audit date:** 2026-09-16  
**Audited durable readiness commit:** `896398c90b0170189cdadd19c12396348e89a37a`  
**Durable closure-evidence commit:** `e7436a62c518de105f700564340b3cdaa6d06080`  
**Closure semantic implementation:** `469841b54f9b3aa0f3e6d3d6b23a804a8f6a57d9`  
**Global invariant:** `ECHO-FREE-TIER-001`

## Scope

This audit recertifies documentation after the near-duplicate grouping and closure-audit semantics were aligned to the frozen `screen -> confirm -> group` contract. It supersedes `CERT-DOC-012` only as current documentation truth. It does **not** certify the corpus, model, thresholds, replay pipeline or real-camera stage.

## Immutable product promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

Camera, RTSP/ONVIF, MQTT, dashboards, persistence and alerts remain supporting capabilities. They do not redefine the acoustic detection/classification core and remain downstream of corpus/model authorization.

## Audited corpus evidence

```text
readiness commit          896398c90b0170189cdadd19c12396348e89a37a
readiness identity        955375c9cc29f2ac5019bb7b2d71090b90734bfe3a8332e5a34698a73ca2d45d
ledger baseline           57869db92f9b8d691d8e7390dd0629e759928b03
ledger entries            1141
fingerprints              1141 / 1141
ledger blockers           0
ledger-summary sha256     cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1
coverage ledger sha256    93be3dceee44df0dfc51ab38c078f1e1e6587ba91e4fbbc53c3b65065e58bfa8
```

## Near-duplicate contract closure

The canonical RMS-envelope fingerprint remains a screening signal, not acoustic identity truth.

```text
candidate threshold                         0.02
confirmed grouping threshold                0.002
max decoded-sample relative delta           0.01
candidate near-duplicate relations           855
candidate cross-group relations              849
confirmed near-duplicate relations             2
confirmed cross-group conflicts after resolve  0
candidate edges rejected by length           835
exact byte duplicate groups                    0
exact canonical-PCM duplicate groups           0
missing fingerprints                            0
```

Review-only screening edges do not participate in transitive connected-component closure. Exact byte/PCM identity and separately confirmed relations remain split-protection evidence. This removes the former artificial mega-components without weakening duplicate protection.

## Structural gates

```text
global acoustic grouping      PASS
global acoustic components       2
members reassigned                4
fallback assets after             0
content merge/delete          false

global dedup                  PASS / gap_codes=[]
recording-family audit        PASS / gap_codes=[]
split integrity               PASS / gap_codes=[]
protected split conflicts        0
quarantined assets               0
eligible development assets   1141
```

No split is manually remapped and no asset is deleted to improve coverage.

## Current final coverage

```text
BACKGROUND
  428 assets / 385 groups / 4 source families                    PASS

FIRE_ALARM
  19 assets / 16 groups / 460.864037 s / 3 source families
  BIGSOUNDBANK 4 / FREESOUND 12 / WIKIMEDIA_COMMONS 3
  train 17 assets / 14 groups
  validation 2 / 2
  test 0 / 0
  HN 202 assets / 202 groups / 4 source families                 PASS

GLASS_SHATTER
  303 assets / 287 groups / 1244.131193 s
  BIGSOUNDBANK 16 / FREESOUND 280
  OPENGAMEART_RUBBERDUCK 6 / OPENGAMEART_TILL_BEHREND 1
  largest source fraction 0.924092                               FAIL <= 0.80
  HN 440 assets / 410 groups / 2 source families                 PASS

SIREN
  169 assets / 169 groups
  HN 235 assets / 235 groups / 4 source families                 PASS

TIRE_SQUEAL
  14 assets / 10 groups / 344.600098 s / 2 source families
  BIGSOUNDBANK 5 / FREESOUND 9
  train 11 assets / 8 groups
  validation 0 / 0
  test 3 assets / 2 groups
  HN 25 assets / 12 groups / 2 source families                   PASS

VEHICLE_HORN
  235 assets / 235 groups
  HN 142 assets / 142 groups / 3 source families                 PASS
```

Asset-quality stop lines remain zero: unknown licenses, missing label provenance, non-positive durations, invalid probes, exact duplicate groups and final near-duplicate groups.

## Coverage gap truth

Coverage remains `FAIL` with exactly **16** empirical gaps:

```text
FIRE_ALARM_ASSETS_BELOW_MIN
FIRE_ALARM_GROUPS_BELOW_MIN
FIRE_ALARM_TEST_ASSETS_BELOW_MIN
FIRE_ALARM_TEST_GROUPS_BELOW_MIN
FIRE_ALARM_TRAIN_ASSETS_BELOW_MIN
FIRE_ALARM_VALIDATION_ASSETS_BELOW_MIN
FIRE_ALARM_VALIDATION_GROUPS_BELOW_MIN
GLASS_SHATTER_SOURCE_CONCENTRATION_TOO_HIGH
TIRE_SQUEAL_ASSETS_BELOW_MIN
TIRE_SQUEAL_GROUPS_BELOW_MIN
TIRE_SQUEAL_TEST_ASSETS_BELOW_MIN
TIRE_SQUEAL_TEST_GROUPS_BELOW_MIN
TIRE_SQUEAL_TRAIN_ASSETS_BELOW_MIN
TIRE_SQUEAL_TRAIN_GROUPS_BELOW_MIN
TIRE_SQUEAL_VALIDATION_ASSETS_BELOW_MIN
TIRE_SQUEAL_VALIDATION_GROUPS_BELOW_MIN
```

The former upstream dedup/family/split failures are closed. Remaining blockers are corpus evidence, not infrastructure ambiguity.

## Quantified acquisition deficits

No split assignment may be manipulated to satisfy these targets. New independent evidence enters the canonical pipeline and deterministic split policy decides placement.

```text
FIRE_ALARM
  assets: 19 / 50       deficit >=31
  groups: 16 / 25       deficit >=9
  train assets: 17 / 20 deficit >=3
  validation: 2/2       needs >=3 assets and >=1 group
  test: 0/0             needs >=5 assets and >=3 groups

TIRE_SQUEAL
  assets: 14 / 50       deficit >=36
  groups: 10 / 25       deficit >=15
  train: 11/8           needs >=9 assets and >=2 groups
  validation: 0/0       needs >=5 assets and >=3 groups
  test: 3/2             needs >=2 assets and >=1 group

GLASS_SHATTER
  Freesound numerator: 280
  current total: 303
  current fraction: 0.924092
  required maximum: 0.80
  minimum total with Freesound fixed at 280: 350
  minimum additional surviving non-Freesound positives: 47
```

`47` is a mathematical lower bound, not an acquisition quota guarantee: dedup/grouping/rights/quality review can reduce surviving credit.

## Freeze and reproducibility

```text
freeze #1         FAIL / only UPSTREAM_COVERAGE_NOT_PASS
freeze #2         FAIL / only UPSTREAM_COVERAGE_NOT_PASS
reproducibility   FAIL / UPSTREAM_FREEZE_NOT_ELIGIBLE
```

Freeze is not promoted early. It becomes eligible only after coverage is genuinely PASS with `gap_codes=[]`.

## Machine-readable readiness

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
CERT-MK1-DF-CORPUS-001 = OPEN
modeling_allowed = false
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
evidence_identity_sha256 = 955375c9cc29f2ac5019bb7b2d71090b90734bfe3a8332e5a34698a73ca2d45d
```

Exact readiness blockers:

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
NO CERT-MK1-DF-CORPUS-001
=
NO Benchmark A/B/C
NO YAMNet/PANNs/CNN model work
NO EMP-MODEL-001
NO threshold calibration
NO replay progression
NO real-camera progression
```

## Authorized next work

```text
independent exact FIRE acquisition
independent exact TIRE acquisition
release-safe non-Freesound GLASS acquisition
  ↓
canonical ledger → grouping → dedup → family → split → coverage
  ↓
coverage PASS / gap_codes=[]
  ↓
freeze #1 → freeze #2 → reproducibility PASS
  ↓
CERT-MK1-DF-CORPUS-001
  ↓
modeling_allowed=true
  ↓
Benchmark A/B/C
```

Evidence-only scouting lanes remain allowed but receive zero corpus, split, coverage or source-diversity credit until reviewed admission and the complete durable cascade succeed.

## Certification decision

`CERT-DOC-013 = CERTIFIED` for documentation truth at the evidence identities above.

`CERT-DOC-001..012` are historical/invalidated. `CERT-MK1-DF-CORPUS-001` remains OPEN. `CERT-MK1-DF-TOOLCHAIN-005` remains CANDIDATE. `CERT-MK1-DF-SONYC-001` remains independently CERTIFIED within scope.

Any change to durable ledger/closure/readiness evidence, promise, taxonomy, source identity, rights, semantic-review decisions, probe/fingerprint/group/dedup/split/coverage/freeze semantics, free-tier invariant or certificate state invalidates DOC-013 and requires re-audit.
