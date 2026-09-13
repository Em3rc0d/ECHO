# MK1 / Arch

## Componentes

```text
source_registry
stream_ingest
preprocess
inference
model_registry
event_engine
messaging
storage
api
observability
provenance
```

## Flujo de runtime

```text
[Source Registry]
       ↓
[Ingestion Adapter] --health--> [Observability]
       ↓ AudioFrame
[Preprocessor]
       ↓ AudioWindow
[Inference Scheduler] <------ [Model Registry]
       ↓ RawInference
[Event Engine] <------------- [Threshold Config]
       ↓ ConfirmedEvent
[Publisher] -----> MQTT
       ↓
[Event Store] <----> [Query API]
```

## Boundaries

### Ingest no sabe ML
Solo entrega frames/ventanas normalizadas con timestamps y source identity.

### Inference no decide alertas
Solo produce scores + metadata del modelo.

### Event Engine no conoce RTSP
Consume inferencias y produce estados/eventos.

### Messaging no decide clasificación
Publica envelopes idempotentes.

## Concurrency

Una fuente = una state machine de stream + buffer independiente. Inference workers se comparten mediante scheduler.

## Failure strategy MK1

- reconnect con backoff;
- source state `ONLINE/DEGRADED/OFFLINE`;
- bounded queue;
- drop policy explícita si el consumidor se atrasa;
- detector no debe crashar porque MQTT no esté disponible;
- publisher debe reportar delivery failure.

## Deployment PoC

Un host local puede contener todos los procesos inicialmente, pero interfaces deben permitir separar workers/broker/storage en MK2.