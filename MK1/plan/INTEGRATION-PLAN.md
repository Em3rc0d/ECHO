# MK1 Integration Plan

**Status:** `READY`

## Integration order

1. ReplaySource -> normalized audio/window golden tests.
2. ModelRunner -> raw inference schema.
3. EventEngine -> deterministic event logs.
4. MQTT publisher/subscriber -> confirmed event delivery.
5. Persistence/query -> E2E evidence.
6. Concurrent replay -> source isolation/backpressure.
7. RTSP adapter -> same downstream pipeline when available.

## Contract tests

Every integration boundary has fixtures: source metadata, audio timing, score vector, event envelope and MQTT payload. Upstream implementation changes should fail contract tests before changing downstream behavior silently.

## Environments

Local deterministic replay environment is the baseline. Camera/LAN adds an environment profile; field evidence always records firmware/device/network context.

## Data migration

Event schema/config changes are versioned. MK1 avoids irreversible persistence design; stored evidence must remain exportable for analysis.

## Failure integration

Inject decoder, inference and broker failures after happy-path integration to verify health and isolation.

## Acceptance

Integrated vertical is not accepted until the same event observed in source replay can be traced through raw inference, EventEngine transition, MQTT message and subscriber/store using stable IDs.

## Invalidation

Breaking contract changes restart integration from the affected boundary.