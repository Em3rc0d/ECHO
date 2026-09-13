# Quarry — Event Engine

**Status:** `CERTIFIED_CONCEPT / PARAMETERS_EMPIRICAL`

## Problem

Models score overlapping windows. Humans/systems care about physical acoustic occurrences. Directly alerting on every positive window creates duplicates, fragmentation and threshold noise.

## Lifecycle

```text
IDLE
  -> CANDIDATE       evidence exceeds entry condition
  -> CONFIRMED       temporal support satisfies rule
  -> ACTIVE          event remains supported
  -> CLOSING         evidence falls below exit condition
  -> CLOSED
  -> COOLDOWN/IDLE
```

The exact internal state names may evolve; the semantic distinction remains.

## State key

At minimum `(source_id, event_type)`. State never crosses sources. Every transition references stream generation/window sequence/timestamp to prevent stale inference after reconnect.

## Parameters

```text
enter_threshold[class]
exit_threshold[class]
M-of-N or equivalent evidence
min_duration
max_gap
merge/dedup window
cooldown/rearm
```

These are fitted/evaluated on validation + continuous replay, not hardcoded by intuition.

## Alternatives

Simple threshold-once has lowest latency but poor stability. M-of-N confirmation is interpretable and robust but may miss very short events. EMA/smoothing can reduce noise but adds temporal memory. Sequence models could learn event boundaries but add training/data complexity. MK1 starts with explicit deterministic aggregation so behavior is auditable.

## Metrics

False alarms/source-hour, physical-event recall, duplicate events per physical event, fragmentation rate, onset/detection latency and event duration error where strong labels exist.

## Pub/Sub boundary

Only confirmed/closed lifecycle outputs become event messages. Raw inference can optionally be logged internally for diagnostics but is not an alarm topic.

## Invalidation

If short-event misses or polyphonic behavior cannot be handled by explicit aggregation, evaluate alternative temporal models while retaining event-envelope semantics.