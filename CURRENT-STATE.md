# Estado actual de ECHO

**Fecha de corte:** 2026-09-14  
**Documento:** estado operativo y de certificación  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Global execution invariant:** `ECHO-FREE-TIER-001`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

La promesa continúa inmutable. Cámaras, RTSP/ONVIF, MQTT, dashboards, persistencia y alertas son soporte; no redefinen el core acústico.

## 2. Development law

ECHO mantiene `brainstorming -> design -> arch -> plan -> build -> test`, acompañado por `mining-site/` y `quarries/`. Ninguna etapa downstream compensa evidencia upstream faltante. Todos los MK heredan `ECHO-FREE-TIER-001`: ruta requerida de 0 USD, sin paid runners/GPU/storage/API/datasets y sin rebajar gates para conseguir PASS.

## 3. Current MK state

```text
MK0 = CERTIFIED

MK1
  brainstorming/design/arch/plan = CLOSED_FOR_BUILD
  build = IN_PROGRESS
    Data Foundry spec             = CERTIFIED
    Data Foundry toolchain        = CERTIFIED_CURRENT_BASELINE
    SONYC v2.3 materialization    = CERTIFIED
    canonical corpus ledger       = MATERIALIZED / OPEN_GATES
    corpus closure readiness      = BLOCKED_FAIL_CLOSED
    model benchmark               = LOCKED_BY_CORPUS_CERT
    replay                        = LOCKED_BY_CORPUS_CERT
    real camera                   = EXTERNAL_GATE + LOCKED_BY_CORPUS_CERT
  milestone = NOT_CERTIFIED

MK2 = GATED_BY_MK1
```

## 4. Current certificate lineage

```text
CERT-MK1-DF-SPEC-001       = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001  = historical
CERT-MK1-DF-TOOLCHAIN-002  = historical
CERT-MK1-DF-TOOLCHAIN-003  = INVALIDATED / historical
CERT-MK1-DF-TOOLCHAIN-004  = CERTIFIED / current
CERT-MK1-DF-SONYC-001      = CERTIFIED / current scoped materialization
CERT-MK1-DF-CORPUS-001     = OPEN

CERT-DOC-001..005           = historical / invalidated for current HEAD
CERT-DOC-006                = CERTIFIED / current
```

`CERT-MK1-DF-TOOLCHAIN-004` binds implementation baseline `ab8c47ba6aabb25390644954a2a06945ca7a81bb` to Data Foundry CI `34922010529` (Python 3.10/3.11/3.12 PASS), Free-Tier `34922010518`, and real SONYC run `34922010537`.

## 5. SONYC v2.3 certified materialization

`CERT-MK1-DF-SONYC-001` certifies the scoped SONYC materialization path:

```text
real SONYC run             34922010537
verified shards            19 / 19 PASS
merge                      PASS
fingerprint contract       PASS
probe failures             0
fingerprint failures       0
durable evidence commit    78fc019839f1c9dad1a58a70d439605d887361d7
```

Fresh materialization summary:

```text
release assets                    18510
release duration seconds          185100.0
target candidate rows             236
confuser candidate rows           428
fingerprinted ledger assets       599
```

This certificate is intentionally narrower than corpus certification. It does not claim final corpus admission, global duplicate/group/split closure, coverage, freeze/reproducibility or model authorization.

## 6. Canonical ledger after SONYC integration

Evidence propagated through:

```text
SONYC durable evidence  78fc019839f1c9dad1a58a70d439605d887361d7
canonical ledger        c93ddb97902b3650921426aaf841473245c7908d
closure audits          311cc2001931d4cceedb90ab5d21f06e15fdf881
closure readiness       de1d31b280e9fad4a3764537aa75d7d72802adb7
```

Authoritative canonical-ledger summary:

```text
status                    PASS_CONSOLIDATED_WITH_OPEN_GATES
ledger entries            1164
canonical fingerprints    1164
fingerprints missing         0
exact SHA-256 dup groups     0
```

Current pre-final positive assets / underlying source families:

```text
FIRE_ALARM       10 / 3
GLASS_SHATTER   304 / 2
SIREN           175 / 3
TIRE_SQUEAL      11 / 2
VEHICLE_HORN    245 / 3
```

Current hard-negative assets / underlying source families:

```text
FIRE_ALARM       34 / 1
GLASS_SHATTER   401 / 1
SIREN            32 / 1
TIRE_SQUEAL       0 / 0
VEHICLE_HORN      0 / 0
```

Canonical fingerprint coverage is complete. That does not imply corpus admission: 531 rows are still `REVIEW_REQUIRED`, 503 rows require the global grouping audit, 83 lack an exact semantic role, and smaller rights/semantic conflict sets remain fail-closed.

## 7. Machine-readable corpus readiness

Authoritative artifact: `MK1/mining-site/materialization/corpus-closure-readiness.json` at commit `de1d31b280e9fad4a3764537aa75d7d72802adb7`.

```text
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
```

Current readiness gap codes are exactly:

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
LEDGER_AUGMENTATION_ONLY_NO_REAL_SOURCE_CREDIT_4
LEDGER_GROUPING_GLOBAL_AUDIT_REQUIRED_503
LEDGER_LICENSE_NOT_RELEASE_SAFE_1
LEDGER_NO_EXACT_SEMANTIC_ROLE_83
LEDGER_RIGHTS_TEXT_CONFLICT_REVIEW_REQUIRED_1
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

These are genuine corpus blockers and are not softened by SONYC/toolchain certification.

## 8. Corpus solidity floor

`MK1-CORPUS-SOLIDITY-001` is unchanged. Per target: assets >=50, groups >=25, independent underlying sources >=2, duration >=180 s, largest source fraction <=0.80; train >=20 assets/10 groups, validation >=5/3, test >=5/3. Global negatives require >=200 assets/50 groups/3 sources. Per-target hard negatives require >=20 assets/10 groups/2 sources.

No broad-label coercion, synthetic independence, duplicate-family inflation, field-holdout leakage, metadata-wrapper double counting or floor reduction is permitted.

## 9. Active corpus-closure sequence

```text
canonical ledger
  -> close rights / exact semantic-role / source-credit conflicts
  -> global exact + cross-format near-duplicate audit
  -> global recording-family/source-independence audit
  -> group-aware split
  -> coverage/diversity/hard-negative PASS with gap_codes=[]
  -> freeze #1 + validate
  -> second clean freeze #2 + validate
  -> semantic identity / reproducibility PASS
  -> EMP-DATASET-001 + EMP-DATA-QUALITY-001
  -> CERT-MK1-DF-CORPUS-001
```

Only after the named corpus certificate does the model-entry gate authorize Benchmark A/B/C.

## 10. Release law — fail closed

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

`scripts/data_foundry/build_corpus_closure_readiness.py --require-modeling-ready` remains non-zero until the corpus predicate is satisfied. `scripts/check_modeling_gate_wiring.py` rejects model/benchmark/train workflow bypasses.

## 11. Frozen target semantics

```text
GLASS_SHATTER
SIREN
FIRE_ALARM
VEHICLE_HORN
TIRE_SQUEAL
```

`BACKGROUND_NO_TARGET` is a training/evaluation state and `UNKNOWN` is a decision-layer abstention. Stop-lines remain strict: Alarm != FIRE_ALARM, Squeak != TIRE_SQUEAL, Car != VEHICLE_HORN, Glassware != GLASS_SHATTER.

## 12. Documentation state

```text
governance/DOCUMENTATION-AUDIT-2026-09-14-SONYC-RECERTIFICATION.md
CERT-DOC-006 = CERTIFIED / current
Markdown corpus = 210 files
```

Documentation certification proves reconstructibility/coherence, not final corpus completion.

## 13. Open nodes

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
EMP-DATASET-001               = OPEN
EMP-DATA-QUALITY-001          = OPEN
CERT-MK1-DF-CORPUS-001       = OPEN
EMP-MODEL-001                 = BLOCKED
EMP-THRESH-001                = BLOCKED
EMP-DIST-001                  = BLOCKED / EXTERNAL FIELD EVIDENCE
EMP-CAP-001                   = OPEN AFTER RUNTIME BUILD
EMP-SLO-001                   = OPEN
EXT-CAMERA-001                = EXTERNAL_GATE_OPEN / NOT AUTHORIZED YET
```

## 14. Next valid transition

```text
CERT-DOC-006                   ✅
CERT-MK1-DF-TOOLCHAIN-004      ✅
CERT-MK1-DF-SONYC-001          ✅
ECHO-FREE-TIER-001              ✅
EMP-MK1-CORPUS-READINESS-001   BLOCKED
        ↓
close exact current corpus gaps
        ↓
global audits + split + coverage + freeze×2 + reproducibility PASS
        ↓
CERT-MK1-DF-CORPUS-001 = CERTIFIED
        ↓
modeling_allowed = true
        ↓
Benchmark A/B/C
```

No downstream shortcut is authorized.

## 15. Invalidation

Changes to promise, taxonomy, source/audio/event contracts, Foundry source/acquisition/mapping/rights/probe/fingerprint/dedup/group/split/coverage/freeze semantics, SONYC persistence, model-entry guard, benchmark set, delivery/privacy rules, `ECHO-FREE-TIER-001`, or audited documentation require dependency review and selective recertification.
