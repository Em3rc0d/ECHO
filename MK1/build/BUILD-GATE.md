# MK1 Build Gate

**Status:** `READY_FOR_REPLAY / CAMERA_BRANCH_EXTERNAL`

## Preconditions satisfied

MK0 certified; v1 taxonomy frozen; source/audio/inference/event contracts defined; A/B/C benchmark frozen; data admission/split rules defined; EventEngine semantics defined; MQTT topics/QoS/idempotency frozen for MK1; privacy/security and test strategy exist.

## Prohibited implementation shortcuts

- single global camera object with no `source_id` abstraction;
- direct model-score -> notification path;
- unbounded audio/inference queues;
- threshold `0.5` or other numeric constants treated as product truth without validation;
- random clip split that violates recording/source grouping;
- test-set tuning;
- credentials/raw dataset committed to Git;
- silent media retention;
- model-specific tensors leaking into public event contract.

## Required first build slices

1. deterministic replay/source/audio contract;
2. model runner common interface;
3. A/B/C experiment path;
4. EventEngine deterministic state machine;
5. MQTT event delivery + idempotent subscriber;
6. multi-source replay and failure observability.

## Camera condition

RTSP adapter can be scaffolded against the source interface, but device-specific success cannot be certified until actual model/stream/network access exists.

## Build completion evidence

Unit/integration tests, reproducible environment, benchmark artifacts, event logs and failure observations must exist before MK1 can move to certification.