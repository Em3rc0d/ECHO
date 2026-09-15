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
  split integrity            = FAIL / 3 protected conflicts
  coverage                   = FAIL
  corpus readiness           = BLOCKED_FAIL_CLOSED
  model/replay/camera        = LOCKED_BY_CORPUS_CERT
MK2 = GATED_BY_MK1
```

All required execution remains 0 USD. Paid fallbacks, label coercion, source-family inflation and lowered quality floors are forbidden.

## 3. Certificate lineage

```text
CERT-MK1-DF-SPEC-001       = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001..003 = historical
CERT-MK1-DF-TOOLCHAIN-004  = INVALIDATED / historical
CERT-MK1-DF-TOOLCHAIN-005  = CANDIDATE
CERT-MK1-DF-SONYC-001      = CERTIFIED / scoped
CERT-MK1-DF-CORPUS-001     = OPEN

CERT-DOC-001..007           = historical / invalidated
CERT-DOC-008                = CERTIFIED / current
```

`TOOLCHAIN-005` stays candidate while closure semantics are still changing. `SONYC-001` remains independently valid because its scoped materialization/fingerprint contract has not changed.

## 4. Post-grouping durable evidence

```text
PR #11 merge                 8c547b70d23ce6c592ddd20d55ff37df9fa7fa03
Data Foundry CI              34969860336 PASS
Documentation Governance     34969860448 PASS
Free-Tier Boundary           34969860642 PASS
canonical ledger run         34969860666 PASS
canonical ledger evidence    9fa3d2f90ddfb731d0921749c921ab2987d54307
closure evidence run         34969945975 PASS
closure evidence             e3e0f58dee3a1602e92f62c8a7708fa1e9fad9ea
readiness run                34970028139 PASS
readiness evidence           8e7702a2bf629642f78859763dabbe09df03df02
```

The evidence pipeline being green does not mean corpus closure is green; it means the current PASS/FAIL evidence is reproducibly materialized.

## 5. Canonical ledger and global grouping

```text
entry_count                         1081
canonical fingerprints              1081 / 1081
fallback assets before grouping      448
fallback assets after grouping         0
global acoustic components            17
members protected by components        97
screened fallback source groups       357
near-duplicate cross-group edges       831
content merge/delete                false
```

Empirical closure:

```text
global-dedup-audit.json       = PASS / gap_codes=[]
recording-family-audit.json   = PASS / gap_codes=[]
```

Remaining ledger blockers are exactly:

```text
LICENSE_NOT_RELEASE_SAFE = 1
SEMANTIC_STATUS_CONFLICT_FIRE_ALARM = 1
SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL = 1
```

Those assets cannot receive final corpus credit unless source evidence resolves them. Exclusion is permitted; coercion is not.

## 6. Split integrity

The acoustic grouping correctly exposed three groups that span recognized source splits:

```text
split-integrity.json = FAIL
original_split_conflict_count = 3
eligible assets without split = 62

conflicting groups:
global-acoustic:49755af077645d9cd379
global-acoustic:683a2c690a388e66903b
global-acoustic:b0a528766144425812e3
```

No seed shopping or manual clip movement is allowed. The safe next transition is policy-governed quarantine of each complete conflicting acoustic component from corpus membership, preserving all source evidence.

## 7. Current coverage truth

Measured final-eligible coverage already exposes genuine acquisition needs:

```text
FIRE_ALARM       9 assets / 6 groups / 190.18 s
TIRE_SQUEAL     11 assets / 11 groups / 280.54 s
GLASS_SHATTER   304 assets, but largest source fraction 0.976974 > 0.80
BACKGROUND      363 assets / 362 groups / only 1 underlying source
```

Hard-negative families:

```text
FIRE_ALARM       26 final-eligible HN / 1 source
GLASS_SHATTER   342 final-eligible HN / 1 source
SIREN            26 final-eligible HN / 1 source
TIRE_SQUEAL       0 / 0
VEHICLE_HORN      0 / 0
```

FIRE_ALARM and TIRE_SQUEAL also fail several train/validation/test asset/group floors. These are real deficits; no floor reduction is authorized.

## 8. Machine-readable readiness

Authoritative artifact at `8e7702a2bf629642f78859763dabbe09df03df02`:

```text
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
evidence_identity_sha256 = fcd07c11d3291d5a78ee28cae93e42de0f16e78522720e78fffb5e71b4bcf129
```

Exact readiness gap codes:

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
SPLIT_INTEGRITY_NOT_PASS
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
corpus-role boundary           PASS
global acoustic grouping      PASS
global dedup                  PASS
recording-family audit        PASS
  ↓
exclude/resolve 3 row blockers
  ↓
quarantine 3 split-conflict acoustic components
  ↓
acquire genuine FIRE_ALARM/TIRE_SQUEAL/negative/source-diversity evidence
  ↓
coverage PASS / gap_codes=[]
  ↓
freeze #1 → freeze #2 → reproducibility PASS
  ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
  ↓
CERT-MK1-DF-CORPUS-001 = CERTIFIED
  ↓
modeling_allowed = true → Benchmark A/B/C
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
governance/DOCUMENTATION-AUDIT-2026-09-15-GROUPING-CLOSURE-008.md
CERT-DOC-008 = CERTIFIED / current
Markdown corpus = 212 files
```

## 13. Invalidation

Changes to promise, taxonomy, source/audio/event contracts, acquisition/mapping/rights/probe/fingerprint/dedup/group/split/coverage/freeze semantics, machine-readable closure evidence, SONYC persistence, model-entry wiring, `ECHO-FREE-TIER-001`, certificate state or audited documentation require dependency review and selective recertification.
