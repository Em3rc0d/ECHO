# Integration Plan — MK1

## File -> core

Primer vertical para aislar ML/event logic de networking.

## RTSP -> core

Se integra tras validar probe/decoder. El adapter entrega el mismo Audio Contract que file.

## Core -> MQTT

El publisher recibe sólo confirmed events. Topic candidate:

```text
echo/v1/{site_id}/{source_id}/events/{event_type}
```

Alert topics se mantienen separados de eventos si se habilitan.

## Consumer contract

Subscribers deben tolerar redelivery y deduplicar por `event_id`. Un test subscriber forma parte del acceptance suite.

## Versioning

`schema_version`, `model_version`, `event_engine_version` y `taxonomy_version` viajan en metadata suficiente para reproducir decisiones.