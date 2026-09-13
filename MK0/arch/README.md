# MK0 / Architecture

**Status:** `CERTIFIED_REFERENCE_ARCHITECTURE`

## Purpose

Architecture translates MK0 design invariants into replaceable components and boundaries without pretending that worker counts, camera codecs or model winners are already known.

## Reference flow

```text
source adapter -> decode/normalize -> bounded source buffer -> windows
-> inference scheduler/runner -> RAW_INFERENCE -> Event Engine
-> CONFIRMED_EVENT -> publisher/store
```

Every layer carries `source_id`; queues/buffers are bounded; the model runner and broker are replaceable behind contracts.

## Artifacts

`INGESTION-OPTIONS.md` evaluates camera/replay ingest. `MODEL-PIPELINE-OPTIONS.md` evaluates representation/runtime paths. `PUBSUB-OPTIONS.md` compares event-delivery choices. `REFERENCE-ARCHITECTURES.md` records PoC and target multi-source topologies.

## Architecture vs experiment

The architecture freezes boundaries, not unsupported numbers. Worker count, buffer seconds, thresholds, model winner and sustainable source count remain benchmark outputs.

## Failure philosophy

Source disconnect, broker outage, inference overload and invalid media are isolated/observable states. A transient failure must not silently mutate event semantics or cause unbounded backlog.

## Invalidation

Revisit if empirical results show the contracts prevent required latency/quality, if camera protocols cannot fit the source abstraction or if product scope adds modalities inside the core.