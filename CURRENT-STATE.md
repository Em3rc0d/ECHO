# Estado actual de ECHO

**Fecha de corte:** 2026-09-15  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Global execution invariant:** `ECHO-FREE-TIER-001`  
**Audited readiness:** `2088c93d65b5d4dff58bb5cdb91b0e76e6288afb`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

La promesa permanece inmutable. Cámaras, RTSP/ONVIF, MQTT, dashboards, persistencia y alertas son soporte; no redefinen el core acústico.

## 2. Camino crítico MK1

```text
Data Foundry / corpus release-safe
  ↓
coverage PASS / gap_codes=[]
  ↓
freeze #1
  ↓
freeze #2 clean
  ↓
reproducibility
  ↓
CERT-MK1-DF-CORPUS-001
  ↓
Benchmark A/B/C
  ↓
modelo ganador
  ↓
Event Engine
  ↓
Edge Agent
  ↓
MQTT + replay E2E
  ↓
real camera
```

No se adelanta modelado, thresholds, replay o cámara antes del certificado de corpus.

## 3. Current MK state

```text
MK0 = CERTIFIED
MK1 planning/design/architecture = CLOSED_FOR_BUILD
MK1 build = IN_PROGRESS
  Data Foundry spec          = CERTIFIED
  SONYC v2.3 materialization = CERTIFIED
  Foundry toolchain          = TOOLCHAIN-005 CANDIDATE
  corpus-role boundary       = PASS
  global acoustic grouping  = PASS
  global dedup               = PASS
  recording-family audit     = PASS
  split integrity            = PASS
  coverage                   = FAIL / 17 detailed gaps
  freeze #1                  = FAIL / gated by coverage
  freeze #2                  = FAIL / gated by freeze #1
  reproducibility            = FAIL / gated by frozen corpus
  corpus readiness           = BLOCKED_FAIL_CLOSED
  model/replay/camera        = LOCKED_BY_CORPUS_CERT
MK2 = GATED_BY_MK1
```

All required execution remains 0 USD. Paid fallbacks, label coercion, source-family inflation, split leakage and lowered quality floors are forbidden.

## 4. Certificate lineage

```text
CERT-MK1-DF-SPEC-001           = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001..003 = historical
CERT-MK1-DF-TOOLCHAIN-004      = INVALIDATED / historical
CERT-MK1-DF-TOOLCHAIN-005      = CANDIDATE
CERT-MK1-DF-SONYC-001          = CERTIFIED / scoped
CERT-MK1-DF-CORPUS-001         = OPEN

CERT-DOC-001..010              = historical / invalidated
CERT-DOC-011                   = CERTIFIED / current
```

## 5. Durable corpus-facing truth

Current durable readiness commit:

```text
2088c93d65b5d4dff58bb5cdb91b0e76e6288afb
```

Canonical ledger:

```text
baseline_commit                       0e05b9ce7ef9afdbd6d0d327922f9811fa0a50d7
entry_count                           1162
canonical fingerprints                1162 / 1162
missing fingerprints                     0
ledger blockers                          0
Wikimedia rows                            7
fallback assets after grouping            0
global acoustic components               14
members reassigned to components         125
content merge/delete                   false
ledger_sha256  b250b18e8ccef3776cdc38d42f240a057bcf99b260cc6cb58a77aad93e9d0cab
```

Structural closure:

```text
global-dedup-audit.json       PASS / gap_codes=[]
recording-family-audit.json   PASS / gap_codes=[]
split-integrity.json          PASS / gap_codes=[]
coverage-gate.json            FAIL / 17 gaps
corpus-freeze-1.validation    FAIL
corpus-freeze-2.validation    FAIL
corpus-reproducibility        FAIL
```

## 6. Split integrity

```text
original split conflicts detected       2
complete groups quarantined             2
assets quarantined                     93
eligible development assets          1069
split-integrity status                PASS
```

Conflicting components remain quarantined as whole acoustic groups. No member is manually remapped or deleted to improve coverage.

## 7. Current final coverage truth

```text
BACKGROUND
  assets 416 / groups 383 / sources 4     PASS

FIRE_ALARM
  assets 12 / groups 9 / duration 311.05767 s
  positive sources 3
    BIGSOUNDBANK 4
    FREESOUND 5
    WIKIMEDIA_COMMONS 3
  train 10 assets / 7 groups
  validation 2 / 2
  test 0 / 0
  HN 206 assets / 206 groups / 4 sources  PASS

GLASS_SHATTER
  final assets 239 / groups 222
  BIGSOUNDBANK 6
  FREESOUND 226
  OPENGAMEART_RUBBERDUCK 6
  OPENGAMEART_TILL_BEHREND 1
  max single-source fraction 0.945607      FAIL <= 0.80 required
  HN 428 assets / 408 groups / 2 sources   PASS

SIREN
  assets 173 / groups 173
  HN 245 assets / 244 groups / 4 sources   PASS

TIRE_SQUEAL
  assets 11 / groups 11 / duration 280.544098 s
  positive sources 2
  train 9 / 9
  validation 0 / 0
  test 2 / 2
  HN 25 assets / 12 groups / 2 sources     PASS

VEHICLE_HORN
  assets 245 / groups 244
  HN 146 assets / 146 groups / 3 sources   PASS
```

Asset quality remains clean: 0 unknown licenses, 0 missing label provenance, 0 invalid probes, 0 non-positive durations, 0 exact duplicate groups and 0 near-duplicate groups in final coverage.

## 8. Detailed coverage gaps

Exactly 17 remain:

```text
FIRE_ALARM_ASSETS_BELOW_MIN
FIRE_ALARM_GROUPS_BELOW_MIN
FIRE_ALARM_TEST_ASSETS_BELOW_MIN
FIRE_ALARM_TEST_GROUPS_BELOW_MIN
FIRE_ALARM_TRAIN_ASSETS_BELOW_MIN
FIRE_ALARM_TRAIN_GROUPS_BELOW_MIN
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

## 9. Machine-readable readiness

```text
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
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

## 10. Frozen solidity law

`MK1-CORPUS-SOLIDITY-001` is unchanged. Per target: >=50 assets, >=25 groups, >=2 independent underlying sources, >=180 s, largest-source fraction <=0.80; train >=20 assets/10 groups, validation >=5/3, test >=5/3. Per-target hard negatives require >=20 assets/10 groups/2 sources. Global negatives require >=200 assets/50 groups/3 sources.

## 11. Active closure sequence

```text
structural gates              PASS
hard-negative floors          PASS
background                    PASS
ledger blockers               CLOSED
  ↓
Freesound exact real FIRE/TIRE acquisition with SHA-bound evidence
GLASS genuine non-Freesound acquisition
  ↓
coverage PASS / gap_codes=[]
  ↓
freeze #1 PASS
  ↓
freeze #2 clean PASS
  ↓
reproducibility PASS
  ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
  ↓
CERT-MK1-DF-CORPUS-001 = CERTIFIED
  ↓
modeling_allowed = true
  ↓
Benchmark A/B/C
```

The Wikimedia FIRE expansion is now durable empirical evidence, not a candidate projection. Future Freesound rows receive zero credit until their own materialization/ledger/closure cascade completes.

## 12. Release law

```text
NO CERT-MK1-DF-CORPUS-001
=
NO Benchmark A/B/C
NO YAMNet/PANNs/CNN model work
NO EMP-MODEL-001
NO threshold calibration
NO replay progression
NO real camera progression
```

## 13. Documentation state

```text
governance/DOCUMENTATION-AUDIT-2026-09-15-CORPUS-CLOSURE-011.md
CERT-DOC-011 = CERTIFIED / current
Markdown corpus = 215 files
```

## 14. Invalidation

Changes to promise, taxonomy, source/audio/event contracts, acquisition/mapping/rights/probe/fingerprint/dedup/group/split/coverage/freeze semantics, machine-readable closure evidence, SONYC persistence, model-entry wiring, `ECHO-FREE-TIER-001`, certificate state or audited documentation require dependency review and selective recertification.
