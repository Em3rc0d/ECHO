# Estado actual de ECHO

**Fecha de corte:** 2026-09-13  
**Documento:** estado operativo y de certificación  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

Esta promesa es inmutable dentro del proyecto. Toda arquitectura, contrato, integración o funcionalidad se evalúa en función de si contribuye a detectar o clasificar eventos acústicos mediante IA. Cámaras, RTSP, ONVIF, brokers, dashboards, bases de datos y alertas son infraestructura de soporte.

## 2. Estado por milestone

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
    data_foundry_foundation = CERTIFIED
    data_corpus_execution   = OPEN
  test           = FOUNDATION_TEST_PASS / FULL_MK1_PENDING
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

## 3. Data Foundry — primer build real de MK1

La transición `READY_NOT_STARTED -> IN_PROGRESS` ya ocurrió. El primer incremento implementado es el Data Foundry, que convierte fuentes heterogéneas en una futura identidad de corpus reproducible antes de permitir benchmarks de modelos.

### Foundation implementada

```text
source registry          ✅
license/use policy       ✅
semantic label mapping   ✅
asset/dataset schemas    ✅
SHA-256 + canonical hash ✅
group-aware splits       ✅
exact-duplicate checks   ✅
metadata quality checks  ✅
source adapters          ✅
admission/quarantine     ✅
manifest generation      ✅
CLI foundation           ✅
CI matrix 3.10/3.11/3.12 ✅
```

Commit de foundation: `586a6320ac45522be1cf475a525ae4713b88e8e8`.  
Commit que añadió CI: `1ad8a4a8635c973722ae69646c8fb6005abcee42`.  
GitHub Actions run: `34741450390`, conclusión `success` en Python 3.10, 3.11 y 3.12; la ejecución 3.11 registró 23 tests `OK`.

### Fuentes registradas

FSD50K, SONYC-UST, SINGA:PURA, ESC-50, UrbanSound8K, AudioSet como referencia/ontology-pretraining, y futuro ECHO Field Dataset. La presencia en el registry no admite automáticamente un asset: derechos, provenance, hash, mapping, calidad, grouping y split siguen siendo gates obligatorios.

### Gaps explícitos

`FIRE_ALARM` y `TIRE_SQUEAL` siguen con gap de corpus release-safe directo en las fuentes seleccionadas. No se fuerza generic `Alarm`, `Screech`, `Friction brake` u otra clase amplia a convertirse en target. La ausencia de datos se conserva como evidencia abierta en vez de contaminar la taxonomía.

## 4. Estado documental

Los depth passes previos siguen válidos para su corpus histórico. La incorporación del Data Foundry modificó materialmente el Markdown corpus, por lo que `CERT-DOC-001` fue invalidado por su propia regla y reemplazado tras re-auditoría por `CERT-DOC-002`.

```text
Root             DEPTH_PASS = PASS
Governance       DEPTH_PASS = PASS
Research         DEPTH_PASS = PASS
MK0              DEPTH_PASS = PASS
MK1              DEPTH_PASS = PASS + Data Foundry extension
MK2              DEPTH_PASS = PASS
Global MD audit  = PASS under CERT-DOC-002
```

La política permanente continúa en `governance/DOCUMENTATION-STANDARD.md` y `governance/DOCUMENTATION-COVERAGE.md`. El audit específico del Foundry está en `governance/DOCUMENTATION-AUDIT-2026-09-13-MK1-FOUNDRY.md`.

## 5. Decisiones congeladas para MK1

`DECISION` ECHO nace lógicamente multi-source aunque la primera validación física pueda usar una sola cámara. Todas las unidades de audio, inferencia, estado y eventos llevan `source_id`.

`DECISION` La ruta primaria de cámara es RTSP; ONVIF se usa como discovery/config cuando esté disponible, sin convertirlo en dependencia obligatoria.

`DECISION` FFmpeg es el decoder/extractor baseline y GStreamer queda como alternativa cuando jitter/reconexión/transport requieran mayor control.

`DECISION` El benchmark mínimo compara A = YAMNet + ECHO head, B = PANNs/Cnn14 + ECHO head y C = CNN compacta log-mel propia.

`DECISION` La taxonomía MK1 v1 usa `GLASS_SHATTER`, `SIREN`, `FIRE_ALARM`, `VEHICLE_HORN`, `TIRE_SQUEAL`; `BACKGROUND_NO_TARGET` es estado de datos y `UNKNOWN` es abstención del decision layer.

`DECISION` La salida target es multi-label; un mismo intervalo puede contener más de un evento.

`DECISION` El lifecycle es `RAW_INFERENCE -> CANDIDATE_EVENT -> CONFIRMED_EVENT -> ALERT/PUBSUB` y las ventanas de inferencia nunca se publican directamente como alarmas.

`DECISION` MQTT/Mosquitto es el bus inicial; confirmed events/alerts usan QoS 1 con `event_id` idempotente porque QoS 1 permite duplicados.

`DECISION` No se retiene audio continuo por defecto, no se incorpora ASR continuo ni identificación de hablantes.

`DECISION` El corpus del benchmark se selecciona únicamente mediante manifiestos Foundry versionados; no existe selección manual silenciosa de archivos.

## 6. Nodos abiertos por evidencia empírica

`EMP-DATASET-001` Corpus admitido: requiere adquisición/ejecución Foundry y counts/durations/groups reales.

`EMP-DATA-QUALITY-001` Calidad/duplicates/diversidad: requiere hashes, probes y auditoría del corpus adquirido.

`CERT-MK1-DF-CORPUS-001` Foundry corpus certificado: requiere DF-G0..DF-G8 para un manifest/profile concreto.

`EMP-MODEL-001` Modelo ganador: requiere ejecutar el benchmark común sobre corpus congelado y comparar calidad, falsas alarmas, latencia y recursos.

`EMP-THRESH-001` Thresholds: deben derivarse del validation set y streaming replay por clase.

`EMP-DIST-001` Distancia/SNR: necesita ensayos reales por distancia, ruido, codec, orientación y dispositivo.

`EMP-CAP-001` Capacidad multi-source: requiere load/soak sobre hardware objetivo; no se promete un número N antes de medir.

`EMP-SLO-001` SLOs finales: se congelan después de obtener evidencia de MK1.

## 7. Gates externos

`EXT-CAMERA-001 = EXTERNAL_GATE_OPEN`. Falta marca/modelo, confirmación de audio, perfil RTSP, posible ONVIF, codec/sample-rate, red, credenciales autorizadas, permisos de prueba y condiciones de captura. Este gate no impide continuar Foundry/replay, pero bloquea claims de campo.

## 8. Siguiente transición autorizada

```text
CERT-MK1-DF-SPEC-001 ✅
        ↓
acquire/parse source releases
        ↓
license + provenance + mapping + hash
        ↓
quality/dedup/group/split
        ↓
freeze corpus manifest
        ↓
CERT-MK1-DF-CORPUS-001
        ↓
ReplaySource / audio pipeline
        ↓
A/B/C benchmark
```

El Foundry foundation está certificado; **el corpus aún no**. El próximo trabajo correcto es producir `EMP-DATASET-001` y `EMP-DATA-QUALITY-001`, no empezar a entrenar con archivos seleccionados a mano.

## 9. Invalidation

Si cambia la promesa, taxonomía, event schema, source/audio contract, benchmark set, Foundry mapping/admission/split semantics, delivery semantics o privacy policy, revisar `governance/CERTIFICATION-DAG.md` y marcar downstream dependiente como `INVALIDATED` hasta revalidación.