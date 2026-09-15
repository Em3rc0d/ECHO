# Estado actual de ECHO

**Fecha de corte:** 2026-09-14  
**Documento:** estado operativo y de certificación  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Global execution invariant:** `ECHO-FREE-TIER-001`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

La promesa permanece inmutable. Cámaras, RTSP/ONVIF, MQTT, dashboards, persistencia y alertas son soporte y no redefinen el core acústico.

## 2. Current MK state

```text
MK0 = CERTIFIED
MK1 planning/design/architecture = CLOSED_FOR_BUILD
MK1 build = IN_PROGRESS
  Data Foundry spec          = CERTIFIED
  SONYC v2.3 materialization = CERTIFIED
  Foundry toolchain          = RECERTIFICATION_REQUIRED / TOOLCHAIN-005 CANDIDATE
  canonical corpus ledger    = MATERIALIZED / OPEN_GATES
  corpus readiness           = BLOCKED_FAIL_CLOSED
  model/replay/camera        = LOCKED_BY_CORPUS_CERT
MK2 = GATED_BY_MK1
```

All execution remains 0 USD under `ECHO-FREE-TIER-001`; paid fallbacks and gate reduction are forbidden.

## 3. Certificate lineage

```text
CERT-MK1-DF-SPEC-001       = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001..003 = historical
CERT-MK1-DF-TOOLCHAIN-004  = INVALIDATED / historical
CERT-MK1-DF-TOOLCHAIN-005  = CANDIDATE
CERT-MK1-DF-SONYC-001      = CERTIFIED / current scoped materialization
CERT-MK1-DF-CORPUS-001     = OPEN

CERT-DOC-001..006           = historical / invalidated
CERT-DOC-007                = CERTIFIED / current
```

Toolchain-004 was invalidated by the material corpus-role-boundary semantics merged in PR #10. Toolchain-005 may not become CERTIFIED until the closure implementation stabilizes and exact Foundry CI, free-tier and empirical cascade evidence are bound.

## 4. SONYC certificate remains valid

```text
run                       34922010537
verified shards           19/19 PASS
probe failures            0
fingerprint failures      0
durable evidence          78fc019839f1c9dad1a58a70d439605d887361d7
```

SONYC certification is scoped and does not certify the final corpus.

## 5. Corpus-role boundary and current ledger

PR #10 merged at `b2fc09b1c98c4c8adcb2fe9dc4db7e1dadc61107` and propagated through:

```text
canonical ledger evidence  3ba3f3141a24013abf8f3cbf68f46043a149ae12
closure audits              4ebbe3f042181ec789d26d1ff4d6ede4ba656ef9
closure readiness           ed069c64d8b5efc855157531a6a59aadff363f40
```

Current corpus-facing ledger:

```text
status                          PASS_CONSOLIDATED_WITH_OPEN_GATES
entry_count                     1081
canonical fingerprints          1081
fingerprints missing               0
role-boundary input rows        1164
review-only rows removed          83
GROUPING_GLOBAL_AUDIT_REQUIRED   448
```

The removed rows remain durable source materialization/review evidence. Materialization alone is not corpus admission.

Positive assets / underlying source families:

```text
FIRE_ALARM       10 / 3
GLASS_SHATTER   304 / 2
SIREN           175 / 3
TIRE_SQUEAL      11 / 2
VEHICLE_HORN    245 / 3
```

Hard-negative assets / underlying source families:

```text
FIRE_ALARM       34 / 1
GLASS_SHATTER   401 / 1
SIREN            32 / 1
TIRE_SQUEAL       0 / 0
VEHICLE_HORN      0 / 0
```

## 6. Current machine-readable readiness

Authoritative artifact: `MK1/mining-site/materialization/corpus-closure-readiness.json` at `ed069c64d8b5efc855157531a6a59aadff363f40`.

```text
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
evidence_identity_sha256 = 6582baef9435283c4e70c25b04c211fb3cf107e752782dfbb9066b897fefff0e
```

Exact audited gap codes:

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
GLOBAL_DEDUP_AUDIT_NOT_PASS
LEDGER_GROUPING_GLOBAL_AUDIT_REQUIRED_448
LEDGER_LICENSE_NOT_RELEASE_SAFE_1
LEDGER_SEMANTIC_STATUS_CONFLICT_FIRE_ALARM_1
LEDGER_SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL_1
RECORDING_FAMILY_AUDIT_NOT_PASS
REPRODUCIBILITY_NOT_PASS
SIREN_HARD_NEGATIVE_SOURCES_1_LT_2
SPLIT_INTEGRITY_NOT_PASS
TIRE_SQUEAL_ASSETS_11_LT_50
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2
VEHICLE_HORN_HARD_NEGATIVES_0_LT_20
VEHICLE_HORN_HARD_NEGATIVE_SOURCES_0_LT_2
```

## 7. Corpus solidity law

`MK1-CORPUS-SOLIDITY-001` is unchanged. Per target: >=50 assets, >=25 groups, >=2 independent underlying sources, >=180 s, largest-source fraction <=0.80; train >=20 assets/10 groups, validation >=5/3, test >=5/3. Per-target hard negatives require >=20 assets/10 groups/2 sources. Global negatives require >=200 assets/50 groups/3 sources.

No broad-label coercion, synthetic independence, wrapper double-counting, duplicate-family inflation or floor reduction is allowed.

## 8. Active closure sequence

```text
corpus-role boundary            PASS / durable
  -> global acoustic grouping   ACTIVE in PR #11
  -> rights/semantic conflicts
  -> real coverage + HN deficits
  -> group-aware split
  -> coverage PASS / gap_codes=[]
  -> freeze #1
  -> freeze #2
  -> reproducibility
  -> EMP-DATASET-001 + EMP-DATA-QUALITY-001
  -> CERT-MK1-DF-CORPUS-001
  -> model-entry
  -> Benchmark A/B/C
```

PR #11 groups exact/near acoustic relations for leakage protection only; it never merges/deletes content or fabricates independent source families. Any original-split conflict exposed by the grouping remains fail-closed.

## 9. Release law

```text
NO CERT-MK1-DF-CORPUS-001
=
NO Benchmark A/B/C
NO model work / EMP-MODEL-001
NO threshold calibration
NO replay progression
NO real camera progression
```

## 10. Documentation state

```text
governance/DOCUMENTATION-AUDIT-2026-09-14-CORPUS-CLOSURE-ITERATION-007.md
CERT-DOC-007 = CERTIFIED / current
Markdown corpus = 211 files
```

## 11. Open empirical nodes

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
EMP-DATASET-001               = OPEN
EMP-DATA-QUALITY-001          = OPEN
CERT-MK1-DF-CORPUS-001       = OPEN
EMP-MODEL-001                 = BLOCKED
EMP-THRESH-001                = BLOCKED
EXT-CAMERA-001                = EXTERNAL_GATE_OPEN / upstream-locked
```

## 12. Invalidation

Changes to promise, taxonomy, source/audio/event contracts, acquisition/mapping/rights/probe/fingerprint/dedup/group/split/coverage/freeze semantics, SONYC persistence, model-entry wiring, `ECHO-FREE-TIER-001`, or audited documentation require dependency review and selective recertification.
