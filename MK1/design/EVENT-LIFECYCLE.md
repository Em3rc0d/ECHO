# Event Lifecycle — MK1

**Status:** `FROZEN_SEMANTICS`

## Purpose

Define the semantic transformation from repeated window scores to one temporal acoustic occurrence.

## Stages

`RAW_INFERENCE`: immutable record of a model/window.  
`CANDIDATE_EVENT`: per-source/type temporal evidence has crossed an entry condition but is not yet confirmed.  
`CONFIRMED_EVENT`: confirmation rule satisfied; event receives stable `event_id`.  
`ACTIVE/CLOSING`: continued evidence or exit hysteresis controls duration.  
`CLOSED`: event no longer active; optional cooldown/rearm prevents immediate duplicate reconfirmation.  
`ALERT/PUBSUB`: downstream routing representation from confirmed event.

## Identity

One physical occurrence should map to one stable event ID despite multiple positive windows and QoS redelivery. Event identity is not the inference-window ID.

## Time semantics

Keep source/window capture time separately from processing/confirmation/publication times so latency can be decomposed. Reconnect changes stream generation; stale prior-generation inference cannot extend a new event.

## Multi-label

Different event types can be active simultaneously on one source. Same event type on different sources has independent lifecycle state.

## Configuration

Entry/exit thresholds, M-of-N/evidence rules, gap/merge/cooldown are versioned Event Engine config derived from validation.

## Metrics

Physical-event recall, false alarms/source-hour, confirmation latency, fragmentation, duplicate events and onset/offset error where labels allow.

## Invalidation

If a future temporal model replaces explicit state logic, preserve these semantic outputs or version the lifecycle contract.