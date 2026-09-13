# Estado actual de ECHO

**Fecha:** 2026-09-13

## Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

## Certification state

```text
MK0 research/design         = CERTIFIED
MK1 DoR (offline/replay)    = CERTIFIED
MK1 build                   = READY / NOT_STARTED
MK1 real-camera branch      = EXTERNAL_GATE_OPEN
MK1 overall                 = NOT_CERTIFIED (build/test pendiente)
MK2 build                   = GATED
```

## Decisiones técnicas cerradas para MK1

- multi-source contracts desde origen;
- PoC físicamente unipunto permitida;
- RTSP source abstraction;
- ONVIF discovery/config opcional;
- FFmpeg baseline, GStreamer fallback/challenger;
- YAMNet A / PANNs Cnn14 B / custom log-mel CNN C;
- multi-label probability contract;
- targets v1: `GLASS_SHATTER`, `SIREN`, `FIRE_ALARM`, `VEHICLE_HORN`, `TIRE_SQUEAL`;
- `BACKGROUND_NO_TARGET` + hard negatives + `UNKNOWN` decision state;
- temporal Event Engine;
- MQTT/Mosquitto;
- QoS1 para confirmed events/alerts + idempotencia por `event_id`;
- no retención de audio continuo por defecto;
- evidence/certification DAG en Git/manifests/CI, no blockchain.

## OPEN / empirical / external

Estos nodos no se pueden cerrar con más lectura de Internet:

- `EXT-CAMERA-001`: cámara real, audio, codec, stream, red y permisos;
- modelo ganador: requiere benchmark;
- thresholds: requiere validation;
- distance/SNR envelope: requiere field test;
- final SLOs: requiere MK1 measurement;
- licencia jurídica del código propio ECHO: decisión explícita del propietario antes de release.

## Qué significa la auditoría

La búsqueda quedó certificada **hasta el límite de lo demostrable documentalmente**. No se han inventado resultados de ML ni hardware. El siguiente nodo ejecutable es `MK1/build`, primero en replay/offline; después, cuando cierre `EXT-CAMERA-001`, se integra y valida la cámara real.