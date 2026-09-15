# Estado actual de ECHO

**Fecha de corte:** 2026-09-15  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Global execution invariant:** `ECHO-FREE-TIER-001`  
**Audited readiness:** `d94eff2958bbe57076610524cbb192d14ec95739`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

La promesa permanece inmutable. Cámaras, RTSP/ONVIF, MQTT, dashboards, persistencia y alertas son soporte; no redefinen el core acústico.

## 2. Estamos en el camino crítico correcto

El primer vertical de MK1 sigue congelado en este orden:

```text
Data Foundry / corpus release-safe
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
cámara real
```

No se debe adelantar UI, cámara, thresholds o integraciones secundarias por encima del cierre del corpus/modelo. La infraestructura solo es prioritaria cuando desbloquea directamente este vertical.

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
  coverage                   = FAIL
  freeze #1                  = FAIL / gated by coverage
  freeze #2                  = FAIL / gated by freeze #1
  reproducibility            = FAIL / gated by frozen corpus
  corpus readiness           = BLOCKED_FAIL_CLOSED
  model/replay/camera        = LOCKED_BY_CORPUS_CERT
MK2 = GATED_BY_MK1
```

All required execution remains 0 USD. Paid fallbacks, label coercion, source-family inflation and lowered quality floors are forbidden.

## 4. Certificate lineage

```text
CERT-MK1-DF-SPEC-001          = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001..003 = historical
CERT-MK1-DF-TOOLCHAIN-004     = INVALIDATED / historical
CERT-MK1-DF-TOOLCHAIN-005     = CANDIDATE
CERT-MK1-DF-SONYC-001         = CERTIFIED / scoped
CERT-MK1-DF-CORPUS-001        = OPEN

CERT-DOC-001..008              = historical / invalidated
CERT-DOC-009                   = CERTIFIED / current
```

`TOOLCHAIN-005` remains candidate while active corpus-closure work can still change Foundry semantics. `SONYC-001` remains independently valid because its scoped materialization/fingerprint contract has not changed.

## 5. Current durable corpus-facing truth

Implementation baseline after PR #15:

```text
4b261bd10d6578a6256fca8ec848ea1055c24b32
```

Current durable readiness commit:

```text
d94eff2958bbe57076610524cbb192d14ec95739
```

Canonical ledger:

```text
entry_count                         1078
canonical fingerprints              1078 / 1078
missing fingerprints                   0
ledger blockers                        0
fallback assets after grouping          0
global acoustic components             17
assets protected by components          97
content merge/delete                 false
```

Current closure nodes:

```text
global-dedup-audit.json       PASS / gap_codes=[]
recording-family-audit.json   PASS / gap_codes=[]
split-integrity.json          PASS / gap_codes=[]
coverage-gate.json            FAIL
corpus-freeze-1.validation    FAIL
corpus-freeze-2.validation    FAIL
corpus-reproducibility        FAIL
```

The former rights/semantic row blockers were quarantined from corpus admission while their source evidence remains durable. No disputed label or non-release-safe license was promoted.

## 6. Split integrity

The three global acoustic components with incompatible protected upstream splits are quarantined as complete groups, not split or manually remapped:

```text
original split conflicts detected     3
complete groups quarantined            3
assets quarantined                    62
split-integrity status              PASS
```

This is the intended fail-closed behavior: leakage protection is preserved, while quarantined evidence cannot satisfy development coverage or frozen-corpus membership.

## 7. Current target precheck

```text
FIRE_ALARM      positives 9 / 50     positive sources 2 / 2    HN 34 / 20    HN sources 1 / 2
GLASS_SHATTER   positives 304 / 50   positive sources 2 / 2    HN 401 / 20   HN sources 1 / 2
SIREN           positives 173 / 50   positive sources 3 / 2    HN 32 / 20    HN sources 1 / 2
TIRE_SQUEAL     positives 11 / 50    positive sources 2 / 2    HN 0 / 20     HN sources 0 / 2
VEHICLE_HORN    positives 245 / 50   positive sources 3 / 2    HN 0 / 20     HN sources 0 / 2
```

This precheck is not the full coverage gate. Final coverage also enforces recording groups, duration, train/validation/test floors, concentration, quality, rights and duplicate controls.

## 8. Machine-readable readiness

Authoritative artifact at `d94eff2958bbe57076610524cbb192d14ec95739`:

```text
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
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

## 9. Frozen solidity law

`MK1-CORPUS-SOLIDITY-001` is unchanged. Per target: >=50 assets, >=25 groups, >=2 independent underlying sources, >=180 s, largest-source fraction <=0.80; train >=20 assets/10 groups, validation >=5/3, test >=5/3. Per-target hard negatives require >=20 assets/10 groups/2 sources. Global negatives require >=200 assets/50 groups/3 sources.

## 10. Active closure sequence

```text
corpus-role boundary         PASS
global acoustic grouping    PASS
global dedup                PASS
recording-family audit      PASS
split integrity             PASS
ledger admission blockers   CLOSED
  ↓
acquire genuine release-safe coverage + HN source diversity
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

Highest-value acquisition deficits are FIRE_ALARM positive coverage, TIRE_SQUEAL positive/HN coverage, a second independent HN source family for FIRE_ALARM/GLASS_SHATTER/SIREN, and real HN corpora for TIRE_SQUEAL/VEHICLE_HORN. Final acquisition quantities must include headroom for dedup/group/split/quality losses rather than target the floors exactly.

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
governance/DOCUMENTATION-AUDIT-2026-09-15-CORPUS-CLOSURE-009.md
CERT-DOC-009 = CERTIFIED / current
Markdown corpus = 213 files
```

## 13. Invalidation

Changes to promise, taxonomy, source/audio/event contracts, acquisition/mapping/rights/probe/fingerprint/dedup/group/split/coverage/freeze semantics, machine-readable closure evidence, SONYC persistence, model-entry wiring, `ECHO-FREE-TIER-001`, certificate state or audited documentation require dependency review and selective recertification.