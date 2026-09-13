# Quarry — Event Engine

**Status:** architecture `CERTIFIED`; numerical parameters `EMPIRICAL / MK1`.

## 1. Problem

Neural models score overlapping windows. Humans and integrations need physical-event-like objects. Publishing every positive window would produce duplicate alarms, unstable toggling and alert floods.

The Event Engine converts:

```text
RAW_INFERENCE -> CANDIDATE_EVENT -> CONFIRMED_EVENT -> CLOSED_EVENT
                                           |
                                           +-> ALERT policy
```

## 2. State key

State is maintained independently by:

```text
(source_id, event_type, model_version, stream_generation)
```

This prevents cross-camera contamination and stale-session mixing.

## 3. Candidate state machine

```text
IDLE
  | evidence crosses enter rule
  v
CANDIDATE
  | temporal confirmation satisfied
  v
ACTIVE / CONFIRMED
  | insufficient evidence for exit duration
  v
CLOSING
  | exit rule satisfied
  v
CLOSED
  | cooldown/rearm
  v
IDLE
```

Exact implementation may simplify states, but semantic transitions must remain explicit.

## 4. Why temporal confirmation matters

A single high score may be a transient confuser. Consecutive/aggregated evidence can reduce false alarms, but excessive confirmation increases detection latency and may miss short events. Therefore `M-of-N`, smoothing and minimum duration are benchmarked rather than guessed.

## 5. Per-class parameters

Candidate parameters:

```text
enter_threshold[class]
exit_threshold[class]
confirmation_rule[class]
max_gap[class]
min_event_duration[class]
merge_gap[class]
dedup_window[class]
cooldown[class]
```

They are versioned configuration, not hard-coded constants.

## 6. Hysteresis

Using separate enter/exit conditions can prevent threshold chatter. Example conceptually:

```text
enter when score/evidence >= T_enter
remain active while evidence >= T_exit
T_exit may be lower than T_enter
```

No numerical values are certified until validation.

## 7. Deduplication semantics

Overlapping model windows belonging to one physical event must generate one confirmed event where possible. Each event receives a stable `event_id`. Re-publication due to broker retries uses the same event identity when it refers to the same event object.

Deduplication is distinct from MQTT QoS duplicate delivery: one is event-formation logic, the other is transport idempotency.

## 8. Simultaneous events

ECHO's inference contract is multi-label. Event states for `SIREN` and `VEHICLE_HORN`, for example, can be active concurrently. Event Engine must not force one winner unless a future taxonomy rule explicitly defines exclusivity.

## 9. Event timestamps

Keep at least:

```text
first_evidence_at
confirmed_at
last_evidence_at
closed_at
source media offsets where available
```

This enables distinction between **acoustic onset**, model confirmation and notification time.

## 10. Confidence summary

A confirmed event may preserve:

```text
peak_score
mean/aggregated_score
number_of_supporting_windows
model_version
threshold_profile_version
```

Do not report a fabricated single “confidence” whose semantics are undocumented.

## 11. Alert separation

A `CONFIRMED_EVENT` is an acoustic inference product. An `ALERT` is a routing/business-policy decision. This separation permits storage/analytics subscribers to consume all events while notification channels only consume selected severity/event classes.

## 12. Metrics

Event Engine tuning is evaluated on continuous replay with:

```text
false alarms/source-hour
missed physical events
duplicate events/physical event
fragmentation rate
merge errors
detection latency
close latency
```

Clip F1 alone is not enough.

## 13. Failure modes

- duplicate alerts from overlapping windows;
- two nearby physical events incorrectly merged;
- one long event fragmented;
- threshold chatter;
- confirmation latency too high;
- cooldown suppressing a legitimate second event;
- state retained after stream generation changes;
- state loss/replay behavior after process restart.

## 14. Closed decisions

- Event Engine exists between inference and Pub/Sub.
- parameters are per class and config-versioned.
- thresholds come from validation evidence.
- multi-label events can coexist.
- event identity is stable and transport-idempotent.

## 15. Invalidation conditions

Revisit if selected model outputs temporal strong predictions rather than window scores, if field evidence shows different event-duration semantics, or if downstream consumers require a different lifecycle contract.
