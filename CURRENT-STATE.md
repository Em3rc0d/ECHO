# Estado actual de ECHO

**Fecha de corte:** 2026-09-16  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Global execution invariant:** `ECHO-FREE-TIER-001`  
**Documentation certificate:** `CERT-DOC-014`

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
Event Engine → Edge Agent → MQTT/replay → real camera
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
  global acoustic grouping   = PASS
  global dedup               = PASS
  recording-family audit     = PASS
  split integrity            = PASS
  split quarantine           = 0 assets
  coverage                   = FAIL / 16 empirical gaps
  freeze #1                  = FAIL / coverage only
  freeze #2                  = FAIL / coverage only
  reproducibility            = FAIL / freeze not eligible
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

CERT-DOC-001..013              = historical / invalidated
CERT-DOC-014                   = CERTIFIED / current
```

## 5. Durable corpus-facing truth

Canonical semantic ledger:

```text
entry_count                           1141
canonical fingerprints                1141 / 1141
missing fingerprints                     0
ledger blockers                          0
fallback assets after grouping            0
global acoustic components                2
members reassigned to components           4
content merge/delete                   false
semantic ledger sha256  cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1
coverage ledger sha256  93be3dceee44df0dfc51ab38c078f1e1e6587ba91e4fbbc53c3b65065e58bfa8
```

`baseline_commit` and the byte hash of the generated ledger summary are **execution provenance**. They remain auditable and must be internally consistent, but they are not the acoustic corpus identity. Readiness v2 binds the semantic `ledger_sha256`, the coverage policy and closure evidence instead.

Current projected readiness semantic identity under DOC-014:

```text
4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
```

## 6. Atomic corpus pipeline

The durable corpus evidence path now has one authoritative writer:

```text
governed source materialization
  ↓
MK1 Canonical Corpus Ledger / atomic orchestrator
  ↓
ledger → grouping → dedup/family/split → coverage
  ↓
freeze #1 → freeze #2 → reproducibility → readiness
  ↓
one atomic durable evidence commit
```

The orchestrator resolves one durable `main` baseline, repeats the complete cascade for byte-level determinism, verifies that `main` did not move, and only then persists the complete evidence set. Repository-token push recursion is not used to chain durable stages.

Standalone closure/readiness workflows are exact-SHA, read-only diagnostics.

## 7. Near-duplicate and split integrity

The broad normalized-RMS threshold is screening only. It is not acoustic identity.

```text
candidate threshold                     0.02
confirmed threshold                    0.002
max decoded-sample delta                0.01
screening candidates                     855
screening candidates cross-group         849
confirmed relations                        2
confirmed cross-group conflicts             0
candidate edges rejected by length       835
exact media duplicate groups                0
exact canonical-PCM duplicate groups        0

global-dedup-audit.json       PASS / gap_codes=[]
recording-family-audit.json   PASS / gap_codes=[]
split-integrity.json          PASS / gap_codes=[]
original split conflicts      0
quarantined assets            0
eligible development assets   1141
```

Review-only screening edges never enter transitive connected-component closure. Exact byte/PCM identity and strict confirmed relations remain split-protection evidence. No split is manually remapped.

## 8. Current final coverage truth

```text
BACKGROUND
  assets 428 / groups 385 / sources 4     PASS

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
  final assets 303 / groups 287 / duration 1244.131193 s
  BIGSOUNDBANK 16
  FREESOUND 280
  OPENGAMEART_RUBBERDUCK 6
  OPENGAMEART_TILL_BEHREND 1
  max single-source fraction 0.924092      FAIL <= 0.80 required
  HN 440 assets / 410 groups / 2 sources   PASS

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

## 9. Detailed coverage gaps

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

All upstream structural audit failures are closed. Background and all target hard-negative floors remain closed.

## 10. Quantified acquisition deficit

```text
FIRE_ALARM
  assets 19/50       minimum asset deficit 31
  groups 16/25       minimum group deficit 9

TIRE_SQUEAL
  assets 14/50       minimum asset deficit 36
  groups 10/25       minimum group deficit 15

GLASS_SHATTER
  current Freesound assets 280
  current total 303
  current concentration 0.924092
  minimum total for 280/total <= 0.80 is 350
  mathematical minimum additional surviving non-Freesound assets = 47
```

These are lower bounds, not permission to manufacture split/source diversity. Every new asset must survive rights, semantics, probe, fingerprint, grouping, dedup and deterministic split assignment.

## 11. Machine-readable readiness

```text
readiness_id = EMP-MK1-CORPUS-READINESS-001
schema = echo.corpus-closure-readiness.v2
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
semantic evidence identity = 4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
```

Exact readiness gaps remain:

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

## 12. Freeze/reproducibility state

```text
freeze #1       FAIL / UPSTREAM_COVERAGE_NOT_PASS only
freeze #2       FAIL / UPSTREAM_COVERAGE_NOT_PASS only
reproducibility FAIL / UPSTREAM_FREEZE_NOT_ELIGIBLE
```

No freeze is promoted while coverage remains red.

## 13. Frozen solidity law

`MK1-CORPUS-SOLIDITY-001` is unchanged. Per target: >=50 assets, >=25 groups, >=2 independent underlying sources, >=180 s, largest-source fraction <=0.80; train >=20 assets/10 groups, validation >=5/3, test >=5/3. Per-target hard negatives require >=20 assets/10 groups/2 sources. Global negatives require >=200 assets/50 groups/3 sources.

## 14. Active closure sequence

```text
structural gates              PASS
hard-negative floors          PASS
background                    PASS
ledger blockers               CLOSED
split quarantine              CLOSED / 0
  ↓
independent exact FIRE acquisition
independent exact TIRE acquisition
release-safe non-Freesound GLASS acquisition
  ↓
atomic canonical corpus cascade
  ↓
coverage PASS / gap_codes=[]
  ↓
freeze #1 PASS → freeze #2 clean PASS → reproducibility PASS
  ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
  ↓
CERT-MK1-DF-CORPUS-001 = CERTIFIED
  ↓
modeling_allowed = true
  ↓
Benchmark A/B/C
```

Evidence-only source materialization is allowed as scouting, but it earns zero corpus credit until reviewed registration/admission and the complete atomic closure cascade succeeds.

## 15. Release law

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

## 16. Documentation state

```text
governance/DOCUMENTATION-AUDIT-2026-09-16-CORPUS-PIPELINE-014.md
CERT-DOC-014 = CERTIFIED / current
Markdown corpus = 218 files
```

## 17. Invalidation

Changes to promise, taxonomy, source/audio/event contracts, acquisition/mapping/rights/probe/fingerprint/dedup/group/split/coverage/freeze semantics, semantic corpus identity, readiness identity contract, SONYC persistence, model-entry wiring, `ECHO-FREE-TIER-001`, certificate state or audited documentation require dependency review and selective recertification.

A pure execution provenance change does not by itself redefine the corpus when all semantic identities and governed evidence remain identical; provenance must nevertheless remain valid and internally consistent.
