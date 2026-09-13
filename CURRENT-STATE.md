# Estado actual de ECHO

**Fecha base:** 2026-09-13

## Resumen

ECHO se encuentra en **research/design-first**. La documentación de MK0, MK1 y MK2 ya no funciona como una colección de README: cada fase contiene artefactos específicos de problema, contratos, arquitectura, planes, riesgos, benchmarks, build gates y test strategy. No existe todavía implementación de producto; el bloqueo es intencional y forma parte de la metodología.

## Promesa inmutable

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

## Cerrado estructuralmente

- evolución `MK0 -> MK1 -> MK2`;
- estructura interna exacta `brainstorming -> design -> arch -> plan -> build -> test`;
- `mining-site` y `quarries` dentro de cada MK;
- arquitectura multi-source desde origen;
- PoC físicamente unipunto permitida sin hardcodear single-source;
- lifecycle `RAW_INFERENCE -> CANDIDATE_EVENT -> CONFIRMED_EVENT -> ALERT`;
- source/audio/event contracts preliminares;
- RTSP como ruta primaria candidata y ONVIF como discovery/config opcional;
- FFmpeg como decoder/extractor baseline;
- MQTT/Mosquitto como Pub/Sub candidate de MK1;
- YAMNet/PANNs/custom CNN como benchmark mínimo, con transformers/SSL como challengers;
- privacy-by-default y no ASR/speaker identification;
- certification DAG y propagación de invalidaciones;
- test design desde antes de build.

## Investigación materializada

MK0 contiene evidencia y líneas de investigación sobre modelos, datasets, streaming, codecs, ONVIF/RTSP, FFmpeg, MQTT, related systems, robustness, OOD, multi-source, security, data acquisition y benchmark design.

MK1 contiene scope cut, demo story, contracts, Event Engine, observability, privacy/security, component boundaries, dataflow, PoC deployment, failure recovery, implementation/training/evaluation/integration plans, build manifest/module/config specs y test matrices E2E.

MK2 contiene production goals, scaling hypotheses, SLO/model governance, multi-source runtime, backpressure, delivery durability, security/observability architecture, scale/CI-CD/model-release/migration/incident plans y load/soak/resilience/regression/release certification.

## Abierto / necesita evidencia

- taxonomía final de MK1 y label mappings;
- licencias exactas de todos los assets/checkpoints seleccionados;
- ejecución del benchmark y modelo ganador;
- thresholds/calibration por clase;
- hardware mínimo certificado;
- marca/modelo/audio/codec/RTSP/ONVIF/red de la cámara real;
- dataset de campo autorizado;
- distancia real y SLOs cuantitativos;
- capacidad N-sources en hardware objetivo.

## Estado de build

```text
MK0/build  = GATED / NOT_STARTED
MK1/build  = GATED / NOT_STARTED
MK2/build  = GATED / NOT_STARTED
```

El siguiente gate correcto es cerrar MK0 con evidencia concreta y resolver los external gates necesarios para certificar el paso hacia MK1/build.