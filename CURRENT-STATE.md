# Estado actual de ECHO

**Fecha de corte:** 2026-09-15  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Global execution invariant:** `ECHO-FREE-TIER-001`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

La promesa permanece inmutable. Cámaras, RTSP/ONVIF, MQTT, dashboards, persistencia y alertas son soporte; no redefinen el core acústico.

## 2. Current MK state

```text
MK0 = CERTIFIED
MK1 planning/design/architecture = CLOSED_FOR_BUILD
MK1 build = IN_PROGRESS
  Data Foundry spec          = CERTIFIED
  SONYC v2.3 materialization = CERTIFIED
  Foundry toolchain          = TOOLCHAIN-005 CANDIDATE
  corpus-role boundary       = PASS
  global dedup               = PASS
  recording-family audit     = PASS
  split integrity            = PASS
  coverage                   = FAIL
  freeze #1/#2               = INELIGIBLE_BY_COVERAGE
  corpus readiness           = BLOCKED_FAIL_CLOSED
  model/replay/camera        = LOCKED_BY_CORPUS_CERT
MK2 = GATED_BY_MK1
```

Todos los paths requeridos mantienen 0 USD. Se prohíben paid fallbacks, coerción de labels, inflación de source families, seed shopping y reducción de floors.

## 3. Certificate lineage

```text
CERT-MK1-DF-SPEC-001       = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001..004 = historical / INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005  = CANDIDATE
CERT-MK1-DF-SONYC-001      = CERTIFIED / scoped
CERT-MK1-DF-CORPUS-001     = OPEN

CERT-DOC-001..008           = historical / invalidated
CERT-DOC-009                = CERTIFIED / current
```

## 4. Durable closure lineage

```text
PR #11 grouping merge       8c547b70d23ce6c592ddd20d55ff37df9fa7fa03
canonical ledger            9fa3d2f90ddfb731d0921749c921ab2987d54307
PR #13 split merge          03cd0627c9c6fcf0780d8d4ce48d5fa7f89fbd01
Data Foundry CI             34971457870 PASS
Free-Tier Boundary          34971457814 PASS
closure evidence run        34971457662 PASS
closure evidence            205eb419b20f10461271ff1fbbd78eb3fa9560e9
readiness run               34971547338 PASS
readiness evidence          589e7f4affed39e1ffcf6f50602d79587560bbb3
```

## 5. Closed technical nodes

```text
canonical fingerprints       1081 / 1081 PASS
global dedup                  PASS / gap_codes=[]
recording-family audit        PASS / gap_codes=[]
split integrity               PASS / gap_codes=[]
```

Split closure uses `MK1-SPLIT-INTEGRITY-002`:

```text
ready candidate assets       1078
quarantined acoustic groups     3
quarantined assets             62
eligible development assets  1016
UNASSIGNED                      0
quarantine identity 1679540dd50eea39200f95ee98130d2e38acd0d21ca73edf7eac04040bb42aaf
```

Los tres grupos conflictivos completos fueron puestos en quarantine. Ningún clip individual se movió entre train/validation/test; los 62 assets siguen disponibles como evidencia pero no cuentan en coverage/freeze.

## 6. Remaining ledger blockers

```text
LICENSE_NOT_RELEASE_SAFE = 1
SEMANTIC_STATUS_CONFLICT_FIRE_ALARM = 1
SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL = 1
```

El siguiente paso autorizado es excluirlos mediante una frontera explícita y auditable, o resolverlos solo con evidencia exacta de origen. No pueden recibir crédito por conveniencia.

## 7. Current coverage truth

`coverage-gate.json = FAIL` sobre 1016 development assets, sin fallos upstream de dedup/group/split.

```text
FIRE_ALARM       9 assets / 6 groups / 190.182749 s
TIRE_SQUEAL     11 assets / 11 groups / 280.544098 s
GLASS_SHATTER   242 assets / 225 groups; FREESOUND=237, BIGSOUNDBANK=5
                largest source fraction=0.979339 > 0.80
BACKGROUND      363 assets / 362 groups / 1 source family
```

Hard negatives finales actuales:

```text
FIRE_ALARM       26 assets / 26 groups / 1 source
GLASS_SHATTER   342 assets / 341 groups / 1 source
SIREN            26 assets / 26 groups / 1 source
TIRE_SQUEAL       0 / 0 / 0
VEHICLE_HORN      0 / 0 / 0
```

FIRE_ALARM y TIRE_SQUEAL fallan además floors de assets/groups por split. Estos déficits requieren media real e independencia acústica genuina; otro wrapper Freesound no crea otra familia.

## 8. Machine-readable readiness

Authoritative artifact: `MK1/mining-site/materialization/corpus-closure-readiness.json` at `589e7f4affed39e1ffcf6f50602d79587560bbb3`.

```text
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
evidence_identity_sha256 = c20eab44bae7cb10e7038833fdf46741d9d4c1574ebfe1b65e47dd6db160249b
```

Exact readiness gaps (19):

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
TIRE_SQUEAL_ASSETS_11_LT_50
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2
VEHICLE_HORN_HARD_NEGATIVES_0_LT_20
VEHICLE_HORN_HARD_NEGATIVE_SOURCES_0_LT_2
```

## 9. Frozen solidity law

`MK1-CORPUS-SOLIDITY-001` no cambia. Per target: assets >=50, groups >=25, independent sources >=2, duration >=180 s, largest source fraction <=0.80; train >=20/10, validation >=5/3, test >=5/3. Per-target HN >=20 assets/10 groups/2 sources. Global background >=200 assets/50 groups/3 sources.

## 10. Active closure sequence

```text
corpus-role boundary        PASS
fingerprints                PASS
global dedup                PASS
recording-family            PASS
split                       PASS
  ↓
exclude/resolve 3 non-admissible ledger rows
  ↓
acquire real positive/background/HN/source-diversity evidence
  ↓
coverage PASS / gap_codes=[]
  ↓
freeze #1 → freeze #2 → reproducibility PASS
  ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
  ↓
CERT-MK1-DF-CORPUS-001 = CERTIFIED
  ↓
modeling_allowed=true → Benchmark A/B/C
```

## 11. Release law

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

## 12. Documentation state

```text
governance/DOCUMENTATION-AUDIT-2026-09-15-SPLIT-CLOSURE-009.md
CERT-DOC-009 = CERTIFIED / current
Markdown corpus = 213 files
```

## 13. Invalidation

Changes to promise, taxonomy, source/audio/event contracts, acquisition/mapping/rights/probe/fingerprint/dedup/group/split/coverage/freeze semantics, machine-readable closure evidence, SONYC persistence, model-entry wiring, `ECHO-FREE-TIER-001`, certificate state or audited documentation require dependency review and selective recertification.
