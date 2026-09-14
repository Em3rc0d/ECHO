# Estado actual de ECHO

**Fecha de corte:** 2026-09-14  
**Documento:** estado operativo y de certificación  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Global execution invariant:** `ECHO-FREE-TIER-001`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

La promesa continúa inmutable. Cámaras, RTSP/ONVIF, MQTT, dashboards, persistencia y alertas son infraestructura de soporte; no redefinen el core acústico.

## 2. Development law

ECHO mantiene el orden:

```text
brainstorming -> design -> arch -> plan -> build -> test
```

con `mining-site/` y `quarries/` para investigación/evidencia. Cada transición importante exige documentación actual, implementación/evidencia cuando corresponde, test y certificado dependiente. Todos los MK heredan `ECHO-FREE-TIER-001`: ruta requerida de 0 USD, sin overages, runners/GPU/storage/API/datasets pagados y sin rebajar gates para conseguir un PASS.

## 3. Milestones

```text
MK0 = CERTIFIED

MK1
  brainstorming/design/arch/plan = CLOSED_FOR_BUILD
  build = IN_PROGRESS
    Data Foundry spec             = CERTIFIED
    Data Foundry toolchain        = CERTIFIED_CURRENT_BASELINE
    canonical corpus ledger       = MATERIALIZED / OPEN_GATES
    corpus closure readiness      = BLOCKED_FAIL_CLOSED
    model benchmark               = LOCKED_BY_CORPUS_CERT
    replay                        = LOCKED_BY_CORPUS_CERT
    real camera                   = EXTERNAL_GATE + LOCKED_BY_CORPUS_CERT
  test = FOUNDRY_GATES_ACTIVE / FULL_MK1_PENDING
  milestone = NOT_CERTIFIED

MK2 = GATED_BY_MK1
```

## 4. Current certificate lineage

```text
CERT-MK1-DF-SPEC-001       = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001  = historical
CERT-MK1-DF-TOOLCHAIN-002  = historical / superseded
CERT-MK1-DF-TOOLCHAIN-003  = CERTIFIED / current
CERT-MK1-DF-CORPUS-001     = OPEN

CERT-DOC-001..004           = historical / superseded for current HEAD
CERT-DOC-005                = CERTIFIED / current
```

`CERT-MK1-DF-TOOLCHAIN-003` binds the readiness/guard implementation baseline `dc225803b5c066b365779fdc2b4b2f0984bb7e19` to Data Foundry CI run `34904125873`, which passed Python 3.10, 3.11 and 3.12. The same baseline passed `ECHO-FREE-TIER-001` in run `34904125820` and deterministic Corpus Closure Readiness generation in run `34904125899`.

The durable readiness evidence was committed as `aac662b770669bf633dd58a582514abcb39c30a1`.

## 5. Canonical corpus ledger

Current compact canonical evidence:

```text
canonical ledger entries = 1048
fingerprints present      = 449
fingerprints missing      = 599
exact SHA-256 duplicate groups = 0
```

Positive counts **before final global dedup/group/split certification**:

```text
GLASS_SHATTER  286
SIREN          170
FIRE_ALARM       5
VEHICLE_HORN   235
TIRE_SQUEAL      5
```

Underlying positive source-family counts:

```text
GLASS_SHATTER 2
SIREN         3
FIRE_ALARM    2
VEHICLE_HORN  3
TIRE_SQUEAL   1
```

Hard-negative counts currently represented by the canonical ledger:

```text
GLASS_SHATTER 401  / source families 1
SIREN          32  / source families 1
FIRE_ALARM     34  / source families 1
VEHICLE_HORN    0  / source families 0
TIRE_SQUEAL     0  / source families 0
```

These are pre-final-audit quantities; they do not imply a certified corpus.

## 6. Machine-readable closure readiness

Authoritative artifact:

```text
MK1/mining-site/materialization/corpus-closure-readiness.json
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
modeling_allowed = false
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
```

The artifact is rebuilt deterministically by `MK1 Corpus Closure Readiness`. It derives `gap_codes` from the canonical ledger, coverage policy and named closure evidence rather than relying on prose.

Current important gaps include:

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

and the final evidence files for global dedup, recording-family audit, split integrity, coverage gate, two freeze validations and reproducibility are not yet PASS.

## 7. Release law — fail closed

The project now enforces, in code and CI:

```text
NO CERT-MK1-DF-CORPUS-001
        =
NO Benchmark A/B/C
NO YAMNet/PANNs/CNN model work
NO EMP-MODEL-001
NO threshold calibration
NO replay pipeline
NO real camera progression
```

`scripts/data_foundry/build_corpus_closure_readiness.py --require-modeling-ready` returns non-zero until the closure evidence is complete, `gap_codes=[]`, and `CERT-MK1-DF-CORPUS-001` itself is `CERTIFIED`.

`.github/workflows/mk1-model-entry-gate.yml` exposes that rule as a reusable workflow. `scripts/check_modeling_gate_wiring.py` rejects future model/benchmark/train workflows that do not wire the corpus gate.

## 8. Corpus solidity floor

`MK1-CORPUS-SOLIDITY-001` remains unchanged.

Per target:

```text
assets >= 50
groups >= 25
underlying independent sources >= 2
duration >= 180 s
largest source fraction <= 0.80
train      >= 20 assets / 10 groups
validation >= 5 assets / 3 groups
test       >= 5 assets / 3 groups
```

Global negatives:

```text
assets >= 200
groups >= 50
sources >= 3
```

Per-target hard negatives:

```text
assets >= 20
groups >= 10
sources >= 2
```

No broad-label coercion, field-holdout leakage, synthetic independence, duplicate-family inflation, metadata-wrapper double counting or floor reduction is permitted.

## 9. Active Corpus Foundry closure sequence

Only this stage is authorized now:

```text
canonical ledger
  -> close rights/semantics/technical evidence
  -> complete canonical fingerprints
  -> materialize independent hard negatives
  -> global exact + cross-format near-duplicate audit
  -> global recording-family/source-independence audit
  -> group-aware split
  -> coverage/diversity PASS with gap_codes=[]
  -> freeze #1 + validate
  -> freeze #2 + validate
  -> semantic identity/reproducibility PASS
  -> EMP-DATASET-001 + EMP-DATA-QUALITY-001
  -> CERT-MK1-DF-CORPUS-001
```

Only after that certificate does the model-entry gate authorize Benchmark A/B/C.

## 10. Frozen target semantics

```text
GLASS_SHATTER
SIREN
FIRE_ALARM
VEHICLE_HORN
TIRE_SQUEAL
```

`BACKGROUND_NO_TARGET` remains a training/evaluation state and `UNKNOWN` remains a decision-layer abstention. Semantic stop-lines remain strict:

```text
Alarm      != FIRE_ALARM
Squeak     != TIRE_SQUEAL
Car        != VEHICLE_HORN
Glassware  != GLASS_SHATTER
```

## 11. Documentation state

Current documentation audit:

```text
governance/DOCUMENTATION-AUDIT-2026-09-14-CORPUS-READINESS.md
CERT-DOC-005 = CERTIFIED
Markdown corpus = 208 files
```

The documentation certificate certifies reconstructibility/coherence, not empirical corpus completion. `CERT-DOC-005` becomes stale if the documented corpus or certification truth changes materially without re-audit.

## 12. Open empirical/external nodes

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
EMP-DATASET-001               = OPEN
EMP-DATA-QUALITY-001          = OPEN
CERT-MK1-DF-CORPUS-001       = OPEN
EMP-MODEL-001                 = LOCKED
EMP-THRESH-001                = LOCKED
EMP-DIST-001                  = LOCKED / EXTERNAL FIELD EVIDENCE
EMP-CAP-001                   = OPEN AFTER RUNTIME BUILD
EMP-SLO-001                   = OPEN
EXT-CAMERA-001                = EXTERNAL_GATE_OPEN / NOT AUTHORIZED YET
```

## 13. Other frozen MK1 decisions

- Logical architecture is multi-source from day one; all audio/inference/event state carries `source_id`.
- RTSP is the primary camera transport; ONVIF is optional discovery/configuration.
- FFmpeg is the baseline decoder/extractor; GStreamer remains an alternative for more demanding transport behavior.
- Benchmark A/B/C remains YAMNet + ECHO head vs PANNs/Cnn14 + ECHO head vs compact log-mel CNN, but is not yet authorized.
- Target output is multi-label.
- Event lifecycle remains `RAW_INFERENCE -> CANDIDATE_EVENT -> CONFIRMED_EVENT -> ALERT/PUBSUB`.
- MQTT/Mosquitto remains the initial event bus; QoS 1 requires idempotent `event_id` handling.
- Continuous ASR/speaker identification and default continuous audio retention remain out of scope.

## 14. Next valid transition

```text
CERT-DOC-005                  ✅
CERT-MK1-DF-TOOLCHAIN-003     ✅
ECHO-FREE-TIER-001             ✅
EMP-MK1-CORPUS-READINESS-001  BLOCKED
        ↓
close only listed corpus gaps
        ↓
readiness eligible_for_certificate_review = true
        ↓
formal corpus certification review
        ↓
CERT-MK1-DF-CORPUS-001 = CERTIFIED
        ↓
readiness modeling_allowed = true
        ↓
Benchmark A/B/C
```

No downstream shortcut is authorized.

## 15. Invalidation

Changes to promise, taxonomy, source/audio/event contracts, Foundry source/acquisition/mapping/rights/probe/fingerprint/dedup/group/split/coverage/freeze semantics, model-entry guard, benchmark set, delivery/privacy rules, `ECHO-FREE-TIER-001`, or audited documentation require dependency review and selective recertification.
