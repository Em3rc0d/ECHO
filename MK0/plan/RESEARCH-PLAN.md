# Research Plan — MK0

## Workstreams

1. **Modelos:** YAMNet, PANNs, custom CNN y challengers modernos.
2. **Datos:** AudioSet ontology, FSD50K, ESC-50, UrbanSound8K, DCASE/DESED, SONYC y datos del dominio.
3. **Streaming:** RTSP/RTP, ONVIF, codecs, FFmpeg/GStreamer.
4. **Event Engine:** smoothing, confirmation, cooldown, dedup, hysteresis, multi-label.
5. **Pub/Sub:** MQTT QoS, idempotencia, persistencia y consumidores.
6. **Robustez:** ruido, SNR, distancia, reverberación, hard negatives, OOD.
7. **Operación:** multi-source, buffers, backpressure, observabilidad, seguridad y privacidad.
8. **Licencias:** código, checkpoints, datasets y assets por separado.

## Salidas obligatorias

Cada workstream debe producir `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION_CANDIDATE`, preguntas abiertas y source URLs.

## Gate

MK0 no cierra hasta que las decisiones que cambiarían arquitectura/taxonomía/datos del primer build estén cerradas o marcadas explícitamente `EXTERNAL_GATE_OPEN`.