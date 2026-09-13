# Event Engine Design — MK1

**Status:** `FROZEN_ARCH-BEHAVIOR / NUMERIC PARAMETERS EMPIRICAL`

## Responsibility

Consume ordered `RAW_INFERENCE` records and maintain state keyed by `(source_id,event_type)` to emit consolidated confirmed/closed events.

## Reference state machine

```text
IDLE
 -> CANDIDATE   score/evidence enters
 -> CONFIRMED   temporal rule satisfied
 -> ACTIVE      evidence persists
 -> CLOSING     below exit rule / gap handling
 -> CLOSED
 -> COOLDOWN/IDLE
```

## Why explicit state

Overlapping windows produce correlated scores. A stateless threshold publisher would duplicate alerts and be unstable around threshold boundaries. Explicit state makes latency/false-positive trade-offs inspectable.

## Parameterization

Per-class `enter_threshold`, optional lower `exit_threshold`, evidence count/window, minimum duration, max gap, merge/dedup window and cooldown. Parameters live in validated config with version/hash.

## Ordering

Process inference monotonically by source/generation/window sequence. Late/out-of-generation records are rejected or recorded as telemetry, not allowed to mutate current state.

## Confidence aggregation

Peak/mean/other aggregation is a configurable policy that must be defined before publishing event confidence. Do not silently reinterpret raw model probability as calibrated event probability.

## Restart behavior

MK1 may reset ephemeral candidate state on process restart; behavior must be explicit. MK2 can persist state if SLOs require it. Duplicate delivery after restart still uses event/idempotency strategy.

## Tests

Boundary scores, short impulses, sustained event, gaps, two close events, simultaneous classes, simultaneous sources, reconnect generation change and deterministic replay.

## Invalidation

If empirical replay shows explicit rules cannot meet recall/false-alarm/latency trade-offs, evaluate learned temporal aggregation while retaining event contract.