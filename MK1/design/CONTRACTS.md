# MK1 Data Contracts

**Status:** `FROZEN_SEMANTICS / MACHINE SCHEMAS IN schemas/`

## Purpose

Separate model internals from runtime/event consumers and make every stage versionable/replayable.

## Raw inference

Represents one model/window output:

```yaml
schema_version: echo.raw_inference.v1
inference_id: ...
source_id: ...
stream_generation: ...
window_id: ...
window_start/end: ...
model_id/model_version: ...
preprocessing_version: ...
scores:
  GLASS_SHATTER: ...
  SIREN: ...
  FIRE_ALARM: ...
  VEHICLE_HORN: ...
  TIRE_SQUEAL: ...
created_at: ...
```

It is diagnostic/model evidence, not a public alert.

## Candidate event

Internal temporal state for one `(source_id,event_type)` with first/last evidence timestamps, peak/aggregate confidence and confirmation counters/state.

## Confirmed event

```yaml
schema_version: echo.event.v1
event_id: globally unique/idempotency key
source_id: ...
site_id: optional
event_type: ...
started_at: ...
confirmed_at: ...
ended_at: optional
confidence: ...
model_version: ...
config_version: ...
taxonomy_version: ...
```

Optional severity is routing/product policy, not ground-truth acoustic class.

## Source state/telemetry

Connection state, stream generation, timestamps, lag, drops, reconnects and decode/inference health are separate schemas. They must not be confused with acoustic events.

## Compatibility

Consumers reject/handle unknown major schema versions explicitly. Additive fields may be backward compatible under documented policy.

## Privacy

No credentials and no raw audio bytes in event/telemetry contracts. Evidence clip references, if later allowed, use access-controlled references and explicit retention policy.

## Validation

JSON Schema tests, golden serialization fixtures, duplicate/idempotency tests and producer/consumer compatibility checks.

## Invalidation

Breaking schema change requires version bump and migration/consumer review.