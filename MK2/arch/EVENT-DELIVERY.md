# MK2 Event Delivery Architecture

**Status:** `DESIGN_SPECIFIED / DURABILITY PROFILE TBD`

## Event truth vs transport

A `CONFIRMED_EVENT` exists independently of whether a broker subscriber has received it. Transport retries/duplicates must not create a new logical event.

## MK1 inheritance

MQTT/Mosquitto with QoS1 and `event_id` idempotency remains baseline. Production requirements determine whether broker persistence plus a local/event-store outbox is necessary.

## Durability alternatives

1. MQTT only — simplest, sufficient if short disconnect semantics meet SLO.
2. Transactional/outbox-like event store + MQTT — preserves local confirmed events for replay/republication.
3. Durable streaming broker (NATS JetStream/RabbitMQ/Redis Streams/Kafka) — justified only by explicit replay/consumer/scale requirements.

## Ordering

Per-source event order may be preserved by publisher/consumer logic where needed. Global ordering across sources is not promised.

## Idempotency

Consumers store/compare `event_id`; republished same logical event keeps identity. Event updates/closure use explicit version/action semantics rather than new IDs accidentally.

## Security

Authenticated publishers, topic ACLs, encrypted transport where required, secret rotation and audit. Source identity in payload is validated against publisher authorization.

## Failure tests

Broker restart/partition, duplicate ack/loss scenarios, slow consumer, outbox replay and schema-version mismatch.

## Invalidation

Choose stronger delivery architecture only if measured SLO/consumer needs exceed baseline.