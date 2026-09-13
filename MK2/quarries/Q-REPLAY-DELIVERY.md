# Quarry — Event Replay, Delivery and Durability

**Status:** MK1 semantics closed; MK2 durability profile `DECISION_BY_REQUIREMENT`.

## 1. Problem

MQTT QoS1 provides at-least-once message delivery semantics but is not, by itself, a durable replayable event ledger for arbitrary offline consumers. MK2 must decide how much history/replay is actually required.

## 2. Distinguish concepts

```text
broker delivery acknowledgement
consumer idempotency
event persistence
consumer replay
ordering
exactly-once business effect
```

These are separate properties.

## 3. Canonical event identity

`event_id` is immutable for one logical confirmed event. Re-delivery/republication uses the same ID so consumers can deduplicate.

## 4. Durability profiles

### Profile A — live-only
MQTT distribution + observability; acceptable where missed history is not a requirement.

### Profile B — durable event store subscriber
Every confirmed event is persisted by an idempotent subscriber/database; consumers query/replay from the store.

### Profile C — replayable streaming infrastructure
Use a broker/log with persistent consumer offsets (e.g. NATS JetStream/Redis Streams/RabbitMQ/Kafka depending measured requirements).

MK2 selects the lowest-complexity profile satisfying product requirements.

## 5. Ordering

Require ordering primarily per `source_id`, not necessarily a total order across all cameras. Cross-source correlation may use timestamps but cannot assume perfectly synchronized camera clocks.

## 6. Failure matrix

Test event generation while:

- broker unavailable;
- broker restarts;
- persistence subscriber unavailable;
- subscriber restarts after acknowledgement boundary;
- duplicate message delivered;
- network partition occurs;
- schema version changes.

## 7. Exactly-once caution

Even if transport offers stronger semantics, external side effects (push notification, database write) require idempotent business logic. ECHO should phrase guarantees precisely rather than marketing “exactly once” without end-to-end proof.

## 8. Release output

Document for each deployment profile:

```text
what can be lost
what can duplicate
retention duration
replay method
ordering guarantee
recovery procedure
```
