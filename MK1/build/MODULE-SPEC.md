# MK1 Module Specification

**Status:** `READY_FOR_IMPLEMENTATION`

## Source module

Input: typed source configuration. Output: timestamped source audio/session health. Must support replay first and RTSP behind same interface.

## Audio module

Input: decoded samples + metadata. Output: normalized samples/windows with deterministic timing. Must expose preprocessing version and avoid persistence by default.

## Model module

Input: window. Output: `RAW_INFERENCE` score vector. A/B/C implementations conform to same interface and expose model/checkpoint identity.

## Scheduler/runtime module

Own bounded queues, source fairness, workers and stale/drop policy. Must expose lag/drop metrics.

## Event module

Input: ordered inference. Output: candidate/confirmed/closed event transitions. State keyed by source/type/generation. Config versioned.

## Messaging module

Input: confirmed event/state/telemetry. Output: MQTT publications with topic/QoS policy. Transport duplicates do not create new event identity.

## Storage/result module

Stores structured run/event/prediction evidence sufficient for evaluation/query. Media storage is separate/disabled by default.

## Observability module

Structured logs/metrics/health without secret/raw-audio leakage.

## Module acceptance

Each module has unit fixtures and boundary contract tests before E2E. No module should depend directly on a concrete implementation that belongs behind another module's interface.