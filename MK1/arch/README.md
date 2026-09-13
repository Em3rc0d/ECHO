# MK1 / Architecture

**Status:** `CLOSED_FOR_BUILD`

## Purpose

Define component/process boundaries that implement the frozen MK1 contracts while allowing replay, RTSP and future scale without rewriting event semantics.

## Reference topology

```text
SourceSupervisor(s)
 -> adapters
 -> normalized per-source buffers
 -> WindowProducer
 -> bounded inference scheduler
 -> model runner(s)
 -> RAW_INFERENCE
 -> EventEngine
 -> CONFIRMED_EVENT
 -> publisher/store
```

## Architecture laws

Source identity is explicit. Buffers/queues are bounded. Failures isolate by source/component. Model runner is replaceable. Event Engine is separate from model. Broker outage is not model failure. Observability crosses every boundary.

## Artifacts

`ARCHITECTURE.md` is the full view; `COMPONENTS.md` owns responsibilities; `DATAFLOW.md` owns record movement; `DEPLOYMENT-POC.md` maps to processes; `MULTISOURCE-BOUNDARY.md` owns concurrency invariants; `FAILURE-RECOVERY.md` owns degraded behavior.

## Output

Plan/build receives stable boundaries but may choose exact Python libraries, worker count and process layout within them.

## Invalidation

Reopen if a frozen design contract cannot be implemented without violating latency, isolation or reproducibility.