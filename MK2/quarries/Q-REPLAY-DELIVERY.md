# Quarry — Replay and Event Delivery

**Status:** `MQTT_BASELINE / PRODUCTION_DURABILITY OPEN`

## Question

What level of event durability/replay is required beyond MK1 MQTT QoS1, and which mechanism achieves it with least operational complexity?

## Requirements to clarify

How long can consumers be offline? Must every confirmed event be recoverable? Is ordering per source required? Are multiple independent consumer groups needed? What duplicate tolerance exists? What is the event retention policy?

## Options

MQTT persistent/session/broker behavior; local event store/outbox + MQTT; NATS JetStream; RabbitMQ; Redis Streams; Kafka. Evaluate only against explicit requirements.

## Preferred evolution

Retain MQTT for live notifications; add durable event store/outbox first if replay/audit is needed but throughput remains modest. Move to durable streaming broker only when consumer/scale requirements justify it.

## Idempotency

Exactly-once-like business behavior relies on stable `event_id` and consumer transaction/idempotency, not simply a broker QoS label.

## Tests

Broker partition/restart, subscriber offline/rejoin, duplicate publish, outbox replay, retention expiry and schema migration.

## Invalidation

Final choice freezes per deployment SLO and can differ between lab and production profiles.