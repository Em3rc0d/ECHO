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
  build          = READY_NOT_STARTED
  test           = NOT_STARTED
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

## 3. Estado documental

El depth pass documental quedó cerrado en todas las zonas y la investigación consolidada de `research/` fue incorporada a `main` antes del audit global.

```text
Root             DEPTH_PASS = PASS
Governance       DEPTH_PASS = PASS
Research         DEPTH_PASS = PASS
MK0              DEPTH_PASS = PASS
MK1              DEPTH_PASS = PASS
MK2              DEPTH_PASS = PASS
Global MD audit  = PASS
Markdown corpus  = 175 files after audit ledger
```

La evidencia archivo por archivo está en `governance/DOCUMENTATION-AUDIT-2026-09-13.md`; la política permanente está en `governance/DOCUMENTATION-STANDARD.md` y `governance/DOCUMENTATION-COVERAGE.md`.

`DOCUMENTATION PASS` significa que los artefactos son reconstructibles y no dependen del chat original para entender propósito, estado, decisiones/evidencia, incertidumbres y reglas de cierre/invalidation. No convierte resultados empíricos pendientes en hechos.

## 4. Decisiones congeladas para MK1

`DECISION` ECHO nace lógicamente multi-source aunque la primera validación física pueda usar una sola cámara. Todas las unidades de audio, inferencia, estado y eventos llevan `source_id`.

`DECISION` La ruta primaria de cámara es RTSP; ONVIF se usa como discovery/config cuando esté disponible, sin convertirlo en dependencia obligatoria.

`DECISION` FFmpeg es el decoder/extractor baseline y GStreamer queda como alternativa cuando jitter/reconexión/transport requieran mayor control.

`DECISION` El benchmark mínimo compara A = YAMNet + ECHO head, B = PANNs/Cnn14 + ECHO head y C = CNN compacta log-mel propia.

`DECISION` La taxonomía MK1 v1 usa `GLASS_SHATTER`, `SIREN`, `FIRE_ALARM`, `VEHICLE_HORN`, `TIRE_SQUEAL`; `BACKGROUND_NO_TARGET` es estado de datos y `UNKNOWN` es abstención del decision layer.

`DECISION` La salida target es multi-label; un mismo intervalo puede contener más de un evento.

`DECISION` El lifecycle es `RAW_INFERENCE -> CANDIDATE_EVENT -> CONFIRMED_EVENT -> ALERT/PUBSUB` y las ventanas de inferencia nunca se publican directamente como alarmas.

`DECISION` MQTT/Mosquitto es el bus inicial; confirmed events/alerts usan QoS 1 con `event_id` idempotente porque QoS 1 permite duplicados.

`DECISION` No se retiene audio continuo por defecto, no se incorpora ASR continuo ni identificación de hablantes.

## 5. Nodos que siguen abiertos por evidencia empírica

`EMP-MODEL-001` Modelo ganador: requiere ejecutar el benchmark común y comparar calidad, falsas alarmas, latencia y recursos.

`EMP-THRESH-001` Thresholds: deben derivarse del validation set y streaming replay por clase.

`EMP-DIST-001` Distancia/SNR: necesita ensayos reales por distancia, ruido, codec, orientación y dispositivo.

`EMP-CAP-001` Capacidad multi-source: requiere load/soak sobre hardware objetivo; no se promete un número N antes de medir.

`EMP-SLO-001` SLOs finales: se congelan después de obtener evidencia de MK1.

## 6. Gates externos

`EXT-CAMERA-001 = EXTERNAL_GATE_OPEN`. Falta marca/modelo, confirmación de audio, perfil RTSP, posible ONVIF, codec/sample-rate, red, credenciales autorizadas, permisos de prueba y condiciones de captura. Este gate no impide iniciar MK1 con dataset/replay, pero bloquea cualquier claim de campo.

## 7. Qué ya NO necesita nueva investigación para habilitar MK1 build

El límite semántico, contratos principales, taxonomía v1, estrategia de datos, benchmark, lifecycle, source abstraction, Pub/Sub, privacy baseline, test strategy y corpus documental están suficientemente cerrados. Reabrirlos requiere nueva evidencia material, no preferencia subjetiva.

## 8. Siguiente transición autorizada

```text
CERT-MK1-READY-001
        ↓
MK1/build — offline/replay vertical
        ↓
MK1/test — metrics + error analysis
        ↓
real-camera branch cuando cierre EXT-CAMERA-001
        ↓
MK1 certification
```

`READY_NOT_STARTED` significa que la implementación está autorizada, no que sus resultados estén certificados.

## 9. Invalidation

Si cambia la promesa, taxonomía, event schema, source/audio contract, benchmark set, delivery semantics, privacy policy o un artefacto documental certificado es reemplazado por contenido insuficiente, revisar `governance/CERTIFICATION-DAG.md` y marcar downstream dependiente como `INVALIDATED` hasta revalidación.