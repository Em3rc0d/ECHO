# Quarry — Pub/Sub

## Candidatos

MQTT/Mosquitto, NATS, Redis Streams, RabbitMQ y Kafka.

## MK1 candidate

MQTT/Mosquitto por:

- Pub/Sub simple;
- self-hosted/open source;
- QoS;
- buen fit IoT/edge;
- baja complejidad operacional para PoC.

## Topics preliminares

```text
echo/v1/{site_id}/{source_id}/events/{event_type}
echo/v1/{site_id}/alerts/{severity}
echo/v1/{site_id}/{source_id}/state
echo/v1/{site_id}/{source_id}/telemetry
```

## Semantics candidate

```text
events: QoS1, retain=false
alerts: QoS1, retain=false
state: QoS1, retain=true
telemetry: QoS0, retain=false
```

QoS1 implica posibles duplicados; `event_id` debe ser idempotency key.

Estado: `CANDIDATE`.