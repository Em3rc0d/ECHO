# Pub/Sub Options — MK0

**Status:** `MQTT_MOSQUITTO_SELECTED_FOR_MK1`

## 1. Requirement

Confirmed acoustic events and source/system state need asynchronous distribution to multiple consumers without coupling the neural network to dashboards, storage or notification code.

## 2. Candidates

### MQTT / Mosquitto

Selected for MK1 because it is lightweight, self-hostable, topic-oriented, widely used for edge/IoT event flows and offers explicit QoS/session semantics. QoS1 is intentionally paired with idempotent `event_id` handling.

### NATS / JetStream

Attractive for lightweight messaging and optional persistence, but introduces another operational path before MK1 needs it. Reconsider in MK2 if durable replay/consumer semantics exceed MQTT design.

### RabbitMQ

Mature queueing/routing and acknowledgements, but heavier than required for the first vertical.

### Redis Streams

Useful stream structure/consumer groups; different operational semantics. Plain Redis Pub/Sub is explicitly unsuitable when disconnected consumers must recover missed messages.

### Kafka

Strong durable log at high scale, but over-complex for the initial source count and PoC operational budget.

## 3. Topic design

```text
echo/v1/{site_id}/{source_id}/events/{event_type}
echo/v1/{site_id}/alerts/{severity}
echo/v1/{site_id}/{source_id}/state
echo/v1/{site_id}/{source_id}/telemetry
```

Topic structure complements, but never replaces, event payload identity/versioning.

## 4. Candidate semantics

Confirmed events/alerts: QoS1, retain=false. Source state: QoS1, retain=true where appropriate. High-rate telemetry: QoS0 unless evidence requires stronger guarantees.

QoS1 means at-least-once; duplicates are legal. Consumers use `event_id` for idempotency. Retained state is not an event history mechanism.

## 5. Failure modes

Broker unavailable, slow subscriber, duplicate delivery, stale retained state, unauthorized publisher, topic explosion and credential leaks. Detector and broker failure domains should be separated enough that a broker outage is visible rather than crashing silently.

## 6. Validation

Tests must cover duplicate publish/delivery, reconnect, retained state, ACL/auth configuration, broker outage and consumer idempotency.

## 7. MK2 trigger

If requirements evolve toward durable multi-consumer replay, exactly-once-like processing or high-volume event logs, evaluate MQTT persistence/outbox versus NATS JetStream/RabbitMQ/Redis Streams/Kafka based on measured need.

## 8. Invalidation

Reopen if consumer delivery/replay SLOs cannot be met with the chosen MQTT design.