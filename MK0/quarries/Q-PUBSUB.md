# Quarry — Pub/Sub

**Status:** `MQTT_MOSQUITTO_CERTIFIED_FOR_MK1`

## Requirement

Decouple acoustic detection from storage/UI/notifications and allow multiple subscribers while preserving event identity and source scope.

## Alternatives

MQTT/Mosquitto selected for MK1. NATS/JetStream, RabbitMQ and Redis Streams remain escalation options for stronger durable replay/queue requirements. Kafka is deferred because first-stage scale does not justify its operational cost. Plain Redis Pub/Sub is rejected for delivery cases requiring disconnected-consumer recovery.

## Topic contract

```text
echo/v1/{site_id}/{source_id}/events/{event_type}
echo/v1/{site_id}/alerts/{severity}
echo/v1/{site_id}/{source_id}/state
echo/v1/{site_id}/{source_id}/telemetry
```

Payload carries schema version, `event_id`, source/site, event type, timestamps, confidence/calibration/model/config identities and optional severity/routing metadata.

## QoS/retain

Events/alerts: QoS1, not retained. State: QoS1 and may be retained. Telemetry: QoS0 by default. QoS1 permits duplicates; consumers deduplicate by `event_id`. Retain is never the event-history mechanism.

## Security

Broker auth/ACL must restrict publishers to allowed topic scopes in field/production. TLS or trusted-network controls depend on deployment. Secrets remain outside Git.

## Failure tests

Duplicate delivery, publisher reconnect, subscriber reconnect, broker restart/outage, unauthorized topic attempt, stale retained state and slow consumer.

## MK2 question

If event loss/replay requirements exceed MQTT session/persistence design, add an outbox/event store or evaluate a durable stream broker using measured requirements.

## Invalidation

Reopen when delivery/replay/ordering/security SLOs cannot be met by the chosen contract.