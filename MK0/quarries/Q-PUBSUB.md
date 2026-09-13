# Quarry — Pub/Sub / Event Distribution

**Status:** MQTT/Mosquitto `CERTIFIED_FOR_MK1`; production durability extensions remain MK2 work.

## 1. Purpose

Decouple acoustic detection from consumers. The neural model must never contain logic such as “send a mobile notification”. ECHO publishes structured events; subscribers decide how to display, persist or act on them.

## 2. Alternatives reviewed

| Technology | Strength | Cost/complexity | ECHO position |
|---|---|---|---|
| MQTT + Mosquitto | lightweight Pub/Sub, QoS, edge/IoT fit, simple self-hosting | limited log/replay semantics compared with streams | **MK1 choice** |
| NATS / JetStream | simple messaging + optional persistence | another operational component | MK2 candidate if replay/durability needs grow |
| RabbitMQ | mature routing/queues | more operational configuration | not needed for MK1 |
| Redis Streams | easy if Redis already exists; durable stream model | additional datastore semantics | candidate, not default |
| Kafka | durable ordered event log at scale | heavy for PoC | unjustified for MK1 |

## 3. Topic namespace

Reference namespace:

```text
echo/v1/{site_id}/{source_id}/events/{event_type}
echo/v1/{site_id}/alerts/{severity}
echo/v1/{site_id}/{source_id}/state
echo/v1/{site_id}/{source_id}/telemetry
```

Topics are routing dimensions; canonical event meaning stays in versioned payload schemas.

## 4. Message classes

### Confirmed events

- QoS 1 candidate/frozen for MK1;
- `retain=false`;
- stable `event_id`;
- consumers must be idempotent.

### Alerts

- derived from confirmed event/policy;
- QoS 1;
- `retain=false` so a new subscriber does not mistake an old alarm for a new occurrence.

### Source state

- state-like information can use retained semantics where appropriate so a subscriber learns current status after subscribing.

### Telemetry

- high-rate/non-critical metrics may use QoS 0 to avoid reliability overhead.

## 5. QoS semantics

MQTT QoS 1 provides **at least once** delivery between client/broker hops under its protocol semantics. Duplicates are possible; therefore `event_id` is an idempotency key. QoS 1 does not by itself certify end-to-end durable business delivery after arbitrary broker/client failure.

Reference: MQTT 5.0 specification: https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html

## 6. Retained messages

Retained messages represent latest state, not event history. ECHO must not use retained event topics as a substitute for an event store.

## 7. Payload contract

A confirmed event should include at least:

```json
{
  "schema_version": "echo.event.v1",
  "event_id": "...",
  "source_id": "CAM-03",
  "site_id": "SITE-01",
  "event_type": "GLASS_SHATTER",
  "first_evidence_at": "...",
  "confirmed_at": "...",
  "peak_score": 0.94,
  "model_version": "...",
  "event_engine_version": "..."
}
```

Exact required fields are governed by `schemas/event.schema.json`.

## 8. Security

For anything beyond an isolated lab:

```text
broker authentication
per-client identity
ACL by topic
TLS where deployment supports it
no shared hard-coded default credentials
secret rotation path
```

A camera/source publisher should not be able to impersonate arbitrary sources if publishers become distributed.

## 9. Failure behavior

Tests must cover:

- broker unavailable at startup;
- broker drops mid-event;
- reconnect and duplicate publish;
- slow subscriber;
- malformed payload rejection;
- incompatible schema version;
- process restart before/after publish acknowledgement.

## 10. Persistence boundary

MK1 can add a durable database subscriber if event history is required. MQTT itself remains the event distribution bus. If MK2 needs replayable event-log semantics, NATS JetStream/Redis Streams/RabbitMQ/Kafka may be re-evaluated from measured requirements.

## 11. Comparable evidence

Frigate exposes per-camera audio status/topics via MQTT, demonstrating an established operational pattern for camera-scoped audio integration: https://docs.frigate.video/integrations/mqtt/ . ECHO's event lifecycle and schemas remain its own design.

## 12. Closed decisions

- MQTT/Mosquitto for MK1.
- QoS1 for confirmed events/alerts.
- consumers are idempotent.
- retained messages are for state, not historical events.
- inference and alert delivery remain separate components.
