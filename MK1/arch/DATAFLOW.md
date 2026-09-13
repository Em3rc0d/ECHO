# MK1 Dataflow

**Status:** `FROZEN_V1`

## 1. Source to window

A configured source starts a stream generation. Adapter output is decoded and normalized, tagged with source/session/timing metadata, buffered with bounded memory and segmented into windows.

## 2. Window to inference

Each window gets `window_id`/sequence and is scheduled fairly. ModelRunner emits a score vector and records model/preprocessing/config identity. Raw inference is immutable evidence for replay/test analysis.

## 3. Inference to event

EventEngine consumes records ordered per source/generation. Threshold/temporal rules update `(source,event_type)` state. Confirmation assigns a stable `event_id`; closure/merge rules define temporal extent.

## 4. Event to delivery

Confirmed event envelope is persisted/logged as configured and published to MQTT. QoS1 redelivery may duplicate transport messages but must not create a second logical event in idempotent consumers.

## 5. Health side-channel

Source connection, decoder quality, buffer/queue lag, inference runtime and broker health travel in state/telemetry channels rather than target-event topics.

## 6. Timing model

Preserve at least capture/media time where reliable, received time, window time, inference completion, confirmation and publication. This allows decomposing network/buffer/model/EventEngine/broker latency.

## 7. Overload

Offline benchmark preserves all windows. Live mode can discard stale work under a versioned policy; dropped work increments source metrics and cannot be silent.

## 8. Privacy

Raw audio samples are transient by default. Persisted result data is structured metadata; optional clips need explicit policy.

## 9. Validation

Golden replay verifies deterministic sequence, schema and event log; concurrent sources verify no identity/state mixing.