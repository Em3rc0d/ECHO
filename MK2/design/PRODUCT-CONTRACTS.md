# Product Contracts — MK2

MK2 conserva compatibilidad conceptual con MK1 y formaliza versioning.

## Contratos estables

- `SourceDescriptor` y source health;
- canonical audio/window metadata;
- `RawInference` interno;
- `ConfirmedEvent` externo;
- `Alert` como proyección de policy;
- metrics/health endpoints;
- model/taxonomy/event-engine manifests.

## Compatibility

Schemas tienen `schema_version`. Cambios aditivos compatibles usan minor; cambios semánticos/incompatibles incrementan major. Consumers deben declarar versiones soportadas.

## Idempotency

`event_id` es estable a través de redeliveries. `delivery_id` puede variar por intento de transporte, separando identidad del evento de identidad del mensaje.