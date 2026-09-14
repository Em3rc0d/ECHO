# Estado actual de ECHO

**Fecha de corte:** 2026-09-13  
**Documento:** estado operativo y de certificación  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Global execution invariant:** `ECHO-FREE-TIER-001`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

Esta promesa es inmutable dentro del proyecto. Toda arquitectura, contrato, integración o funcionalidad se evalúa en función de si contribuye a detectar o clasificar eventos acústicos mediante IA. Cámaras, RTSP, ONVIF, brokers, dashboards, bases de datos y alertas son infraestructura de soporte.

## 2. Principio de desarrollo

ECHO es documentation-first y evidence-first:

```text
brainstorming -> design -> arch -> plan -> build -> test
```

con `mining-site/` y `quarries/` como capas de investigación/evidencia.

Un nodo no se certifica porque “parece terminado”. Debe tener documentación coherente, criterios de aceptación previos, implementación/evidencia cuando aplique, trazabilidad de inputs/outputs e invalidation rules.

Todos los MK heredan `ECHO-FREE-TIER-001`: $0 required path, sin overages, servicios/APIs/storage/GPU/runners pagados y sin degradar los gates para caber gratis.

## 3. Estado por milestone

```text
MK0
  brainstorming  = CERTIFIED
  design         = CERTIFIED
  arch           = CERTIFIED
  plan           = CERTIFIED
  build          = research-artifacts only
  test           = CERTIFIED
  milestone      = CERTIFIED

MK1
  brainstorming  = CLOSED_FOR_BUILD
  design         = CLOSED_FOR_BUILD
  arch           = CLOSED_FOR_BUILD
  plan           = CLOSED_FOR_BUILD
  build          = IN_PROGRESS
    data_foundry_spec             = CERTIFIED
    data_foundry_toolchain        = CERTIFIED_CURRENT_BASELINE
    corpus_foundry_closure        = IN_PROGRESS
    replay_audio_vertical         = BLOCKED_BY_CERTIFIED_CORPUS
  test           = DATA_FOUNDRY_TOOLCHAIN_PASS / FULL_MK1_PENDING
  milestone      = NOT_CERTIFIED

MK2
  brainstorming  = SPECIFIED
  design         = SPECIFIED
  arch           = SPECIFIED
  plan           = SPECIFIED
  build          = GATED
  test           = GATED
  milestone      = GATED_BY_MK1
```

## 4. Data Foundry certification state

Current certificates:

```text
CERT-MK1-DF-SPEC-001       = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001  = historical / superseded for current baseline
CERT-MK1-DF-TOOLCHAIN-002  = CERTIFIED
CERT-MK1-DF-CORPUS-001     = OPEN
```

`CERT-MK1-DF-TOOLCHAIN-002` binds the current engineering baseline `be75a4323ec67f7c9528cbdbf6a06a8524494501` to GitHub Actions run `34800084225`. The matrix passed Python 3.10/3.11/3.12; the Python 3.11 job ran **67 tests** successfully.

This certifies the executable Foundry foundation, not the final real corpus.

## 5. Corpus Foundry Closure — active critical path

Deep research after the earlier toolchain certification exposed final-corpus requirements that must remain visible. Therefore it is no longer correct to describe DF-G0..DF-G8 as having no remaining implementation/integration work.

The authoritative closure runbook is:

```text
MK1/build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md
```

The remaining internal closure nodes are:

```text
1. canonical global asset ledger
2. per-asset rights + semantic closure for admitted release_safe assets
3. bounded hard-negative materialization + admission evidence
4. cross-format/transcode-aware near-duplicate hardening
5. near-duplicate positive/negative fixture validation
6. global recording-family/source-independence audit
7. group-aware split feasibility against all class/split floors
8. coverage/diversity/hard-negative PASS on real admitted corpus
9. frozen bundle validation
10. second clean freeze + identity comparison
11. final corpus certificate emission only if every ancestor gate passes
```

These are real closure requirements, not optional enhancements.

## 6. Dataset materialization state

Materialization is executed under the global zero-cost boundary, not through a monolithic paid/persistent data lake.

Canonical pattern:

```text
bounded shard / public asset batch
  -> verify
  -> observe real bytes
  -> hash + probe + provenance
  -> emit compact evidence
  -> delete raw bytes
  -> next batch
```

Current evidence includes bounded/sharded publisher execution and public per-asset gap materialization. Downloaded/candidate counts do not equal admitted corpus counts.

`FSD50K` full multipart audio is not a mandatory release-safe dependency. Official metadata/ground truth plus defensible current per-asset acquisition may be used without treating the same underlying recording as two independent sources.

## 7. Frozen semantic boundary

MK1 targets:

```text
GLASS_SHATTER
SIREN
FIRE_ALARM
VEHICLE_HORN
TIRE_SQUEAL
```

`BACKGROUND_NO_TARGET` is a training/evaluation state. `UNKNOWN` is decision-layer abstention.

Semantic stop-lines remain:

```text
Alarm      != FIRE_ALARM
Squeak     != TIRE_SQUEAL
Car        != VEHICLE_HORN
Glassware  != GLASS_SHATTER
```

`FIRE_ALARM` and `TIRE_SQUEAL` remain the highest-risk data nodes until the actual admitted/diverse corpus evidence passes.

## 8. Corpus solidity floor

`MK1-CORPUS-SOLIDITY-001` is an engineering certification floor, not a guarantee of model performance.

Per target:

```text
assets >= 50
groups >= 25
independent underlying sources >= 2
duration >= 180 s
largest source fraction <= 0.80
train      >= 20 assets / 10 groups
validation >= 5 assets / 3 groups
test       >= 5 assets / 3 groups
```

Global negative pool:

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

No field-holdout, synthetic inflation, duplicate recording, metadata wrapper or broad semantic mapping may be used to fake those floors.

## 9. Corpus certificate predicate

`CERT-MK1-DF-CORPUS-001` remains `OPEN` until the real named `release_safe` corpus provides:

```text
source/provenance PASS
rights PASS
semantic/review PASS
real-byte/hash/probe PASS
hard-negative PASS
exact duplicate leakage = 0
near-duplicate leakage = 0
recording-family cross-split leakage = 0
field holdout contamination = 0
coverage/diversity PASS
gap_codes = []
bundle validation PASS
second-freeze reproducibility PASS
ECHO-FREE-TIER-001 PASS
```

Exact real counts, durations, diversity and duplicate findings belong to empirical evidence nodes and are not inferred from source metadata.

## 10. Documentation state

Documentation remains an upstream certification gate.

The previous documentation certificate `CERT-DOC-003` covered the 197-file corpus at commit `7ef9c1d52b12396e6e73f00f0a3a442d49061fe3`. Substantive corpus-closure/free-tier documents were added afterward, so `CERT-DOC-003` is historical/stale for current HEAD by its own invalidation rule.

A new delta/full coherence audit is being recorded as `CERT-DOC-004`. Until that audit is finalized in governance, current documentation state is:

```text
CERT-DOC-001  historical
CERT-DOC-002  historical
CERT-DOC-003  historical / superseded for current HEAD
CERT-DOC-004  CANDIDATE_PENDING_AUDIT
```

No engineering certificate is allowed to hide a documentation contradiction.

## 11. Other frozen MK1 decisions

`DECISION` ECHO nace lógicamente multi-source aunque la primera validación física pueda usar una sola cámara. Todas las unidades de audio, inferencia, estado y eventos llevan `source_id`.

`DECISION` La ruta primaria de cámara es RTSP; ONVIF se usa como discovery/config cuando esté disponible, sin convertirlo en dependencia obligatoria.

`DECISION` FFmpeg es el decoder/extractor baseline y GStreamer queda como alternativa cuando jitter/reconexión/transport requieran mayor control.

`DECISION` El benchmark mínimo compara A = YAMNet + ECHO head, B = PANNs/Cnn14 + ECHO head y C = CNN compacta log-mel propia.

`DECISION` La salida target es multi-label; un mismo intervalo puede contener más de un evento.

`DECISION` El lifecycle es `RAW_INFERENCE -> CANDIDATE_EVENT -> CONFIRMED_EVENT -> ALERT/PUBSUB` y las ventanas de inferencia nunca se publican directamente como alarmas.

`DECISION` MQTT/Mosquitto es el bus inicial; confirmed events/alerts usan QoS 1 con `event_id` idempotente porque QoS 1 permite duplicados.

`DECISION` No se retiene audio continuo por defecto, no se incorpora ASR continuo ni identificación de hablantes.

`DECISION` El corpus del benchmark se selecciona únicamente mediante manifests Foundry versionados y validados; no existe selección manual silenciosa de archivos.

## 12. Nodos empíricos abiertos

```text
EMP-DATASET-001      = OPEN
EMP-DATA-QUALITY-001 = OPEN
CERT-MK1-DF-CORPUS-001 = OPEN
EMP-MODEL-001        = OPEN
EMP-THRESH-001       = OPEN
EMP-DIST-001         = OPEN
EMP-CAP-001          = OPEN
EMP-SLO-001          = OPEN
```

Model winner, thresholds, latency/capacity envelope and field performance cannot be certified before their required empirical execution.

## 13. External gates

`EXT-CAMERA-001 = EXTERNAL_GATE_OPEN`.

Real-camera claims require authorized device/site evidence. This does not block corpus closure or offline replay, but it does block field certification.

## 14. Next authorized transition

```text
DOCUMENTATION COHERENCE / CERT-DOC-004
        ↓
CERT-MK1-DF-TOOLCHAIN-002 ✅
        ↓
MK1 CORPUS FOUNDRY CLOSURE
        ↓
EMP-DATASET-001 + EMP-DATA-QUALITY-001
        ↓
CERT-MK1-DF-CORPUS-001
        ↓
benchmark A/B/C
        ↓
EMP-MODEL-001 + calibration/threshold evidence
        ↓
Temporal Event Engine
        ↓
offline + multi-source replay/resource tests
        ↓
real capture external gate
        ↓
MK1 end-to-end certification decision
```

## 15. Invalidation

Si cambia la promesa, taxonomía, source/audio/event contract, benchmark set, Foundry source/acquisition registry semantics, mapping/admission/review/probe/dedup/split/manifest/handoff semantics, delivery semantics, privacy policy, free-tier boundary or audited documentation corpus, revisar `governance/CERTIFICATION-DAG.md` y marcar los dependientes afectados como `INVALIDATED` hasta revalidación.