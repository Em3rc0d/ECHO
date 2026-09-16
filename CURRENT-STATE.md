# Estado actual de ECHO

**Fecha de corte:** 2026-09-16  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Global execution invariant:** `ECHO-FREE-TIER-001`  
**Audited readiness:** `48af9f220b30f2197aa376bff025195cb0a2a13b`

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
  coverage                   = FAIL / 16 detailed gaps
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

CERT-DOC-001..011              = historical / invalidated
CERT-DOC-012                   = CERTIFIED / current
```

## 5. Durable corpus-facing truth

Current durable readiness commit:

```text
48af9f220b30f2197aa376bff025195cb0a2a13b
```

Canonical ledger:

```text
baseline_commit                       050f2ebc39fea0d1e6903190ad471fd97d1487dc
entry_count                           1141
canonical fingerprints                1141 / 1141
missing fingerprints                     0
ledger blockers                          0
fallback assets after grouping            0
global acoustic components               12
members reassigned to components         118
content merge/delete                   false
ledger_sha256  1ab3712452f42205fe9004f1d6cb9e778297487891bb373e5c42d635854f1d85
```

The count reduction versus DOC-011 is accepted external-evidence drift from live Freesound rematerialization. Stale pages/previews were not preserved just to keep corpus counts high.

Structural closure:

```text
global-dedup-audit.json       PASS / gap_codes=[]
recording-family-audit.json   PASS / gap_codes=[]
split-integrity.json          PASS / gap_codes=[]
coverage-gate.json            FAIL / 16 gaps
corpus-freeze-1.validation    FAIL
corpus-freeze-2.validation    FAIL
corpus-reproducibility        FAIL
```

## 6. Split integrity

```text
original split conflicts detected       2
complete groups quarantined             2
assets quarantined                     93
eligible development assets          1048
split-integrity status                PASS
```

Conflicting components remain quarantined as whole acoustic groups. No member is manually remapped or deleted to improve coverage.

## 7. Current final coverage truth

```text
BACKGROUND
  assets 416 / groups 383 / sources 4     PASS

FIRE_ALARM
  assets 19 / groups 16 / duration 460.864037 s
  positive sources 3
    BIGSOUNDBANK 4
    FREESOUND 12
    WIKIMEDIA_COMMONS 3
  train 17 assets / 14 groups
  validation 2 / 2
  test 0 / 0
  HN 202 assets / 202 groups / 4 sources  PASS

GLASS_SHATTER
  final assets 222 / groups 205
  BIGSOUNDBANK 6
  FREESOUND 209
  OPENGAMEART_RUBBERDUCK 6
  OPENGAMEART_TILL_BEHREND 1
  max single-source fraction 0.941441      FAIL <= 0.80 required
  HN 428 assets / 408 groups / 2 sources   PASS

SIREN
  assets 169 / groups 169
  HN 235 assets / 235 groups / 4 sources   PASS

TIRE_SQUEAL
  assets 14 / groups 10 / duration 344.600098 s
  positive sources 2
    BIGSOUNDBANK 5
    FREESOUND 9
  train 11 assets / 8 groups
  validation 0 / 0
  test 3 assets / 2 groups
  HN 25 assets / 12 groups / 2 sources     PASS

VEHICLE_HORN
  assets 235 / groups 235
  HN 142 assets / 142 groups / 3 sources   PASS
```

Asset quality remains clean: 0 unknown licenses, 0 missing label provenance, 0 invalid probes, 0 non-positive durations, 0 exact duplicate groups and 0 near-duplicate groups in final coverage.

## 8. Detailed coverage gaps

Exactly 16 remain:

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

`FIRE_ALARM_TRAIN_GROUPS_BELOW_MIN` is now closed. Background and all target hard-negative floors remain closed.

## 9. Machine-readable readiness

```text
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
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

## 10. Frozen solidity law

`MK1-CORPUS-SOLIDITY-001` is unchanged. Per target: >=50 assets, >=25 groups, >=2 independent underlying sources, >=180 s, largest-source fraction <=0.80; train >=20 assets/10 groups, validation >=5/3, test >=5/3. Per-target hard negatives require >=20 assets/10 groups/2 sources. Global negatives require >=200 assets/50 groups/3 sources.

## 11. Active closure sequence

```text
structural gates              PASS
hard-negative floors          PASS
background                    PASS
ledger blockers               CLOSED
  ↓
independent exact FIRE acquisition / split coverage
independent exact TIRE acquisition / split coverage
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

Evidence-only source materialization is allowed as scouting, but it earns zero corpus credit until reviewed registration/admission and the complete ledger/closure cascade succeed.

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
governance/DOCUMENTATION-AUDIT-2026-09-16-CORPUS-CLOSURE-012.md
CERT-DOC-012 = CERTIFIED / current
Markdown corpus = 216 files
```

## 14. Invalidation

Changes to promise, taxonomy, source/audio/event contracts, acquisition/mapping/rights/probe/fingerprint/dedup/group/split/coverage/freeze semantics, machine-readable closure evidence, SONYC persistence, model-entry wiring, `ECHO-FREE-TIER-001`, certificate state or audited documentation require dependency review and selective recertification.
