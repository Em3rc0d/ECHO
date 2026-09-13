# MK1 Scope Cut

**Status:** `CLOSED`

## Objective

Deliver the smallest end-to-end vertical that can generate defensible evidence about ECHO's acoustic detection/classification promise.

## IN

- replay/file source adapter and common source contract;
- real RTSP adapter when external access is available;
- normalized audio pipeline;
- v1 five-target multi-label taxonomy;
- A/B/C model benchmark;
- validation-derived per-class thresholds;
- explicit `UNKNOWN`/background behavior;
- temporal Event Engine;
- confirmed event schema;
- MQTT/Mosquitto publisher and subscriber;
- source/runtime telemetry;
- reproducible manifests/hashes;
- long-stream replay evaluation;
- logical multi-source concurrency with N replay sources;
- privacy/security baseline.

## OUT / DEFERRED

- production distributed cluster;
- arbitrary camera fleet support guarantees;
- advanced acoustic localization;
- speech recognition/speaker identity;
- video fusion;
- full commercial dashboard/mobile UX;
- complex OOD methods before baseline evidence;
- Kafka-scale event platform;
- automatic model retraining/online learning;
- final SLOs or guaranteed field distance before measurement.

## Why this cut is sufficient

It exercises every semantic boundary from audio source to confirmed event and produces the empirical data required to design MK2. Deferred items can be added behind existing source/model/publisher contracts.

## Failure criterion

If the build cannot achieve useful event behavior without changing source/event semantics, MK1 exposes a design flaw and the relevant upstream certificate must reopen.

## Invalidation

Any added requirement that changes taxonomy, lifecycle or core source contract requires explicit scope/gate review.