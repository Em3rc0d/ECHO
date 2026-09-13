# MK2 Resilience Architecture

## Source reconnect

```text
failure
  ↓
mark DEGRADED
  ↓
close broken decoder/session
  ↓
backoff + jitter
  ↓
new stream_session_id
  ↓
reconnect
```

No reutilizar silently timestamps/session state de una conexión anterior.

## Backpressure

Cuando inference no alcanza ingest:

1. medir queue lag;
2. aplicar policy por source;
3. preservar fairness;
4. preferir datos recientes si el caso realtime lo requiere;
5. registrar dropped windows;
6. degradar health state.

## Broker failure

Detection no debe caer porque MQTT esté offline. MK2 evalúa una de estas estrategias:

```text
bounded local outbox
persistent outbox
retry with backoff
```

La selección depende del delivery SLO.

## Storage failure

Pub/Sub y persistencia no deben compartir un único failure point si no es necesario. Definir orden y compensación: persist-first, publish-first o transactional/outbox; benchmarkear costo.

## Model failure

- model artifact hash mismatch => fail closed;
- incompatible schema/preprocess => reject activation;
- rollback to last certified model;
- warm-up before traffic.

## Config failure

Config inválida no entra en runtime. Validation ocurre antes de activation.