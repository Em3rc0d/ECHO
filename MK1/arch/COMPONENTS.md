# Components — MK1

## `source-registry`

Carga descriptors y ciclo de vida de fuentes.

## `ingestion`

Adapters `file/rtsp/microphone`, decoder y normalización.

## `windowing`

Buffers acotados por source y ventanas con timestamps reproducibles.

## `inference`

Interfaz común para YAMNet/PANNs/custom candidates. No conoce MQTT.

## `event-engine`

Estado temporal por source/clase; genera confirmed events.

## `publisher`

Serializa schema versionado y publica en MQTT.

## `event-store` (opcional MK1)

Persistencia de metadata para evaluación; no es source of truth del audio.

## `telemetry`

Métricas/logging/health.

## Boundaries

Dependencias fluyen hacia contracts/domain; adapters externos no deben definir entidades core.