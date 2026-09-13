# Quarry — Latency

**Status:** measurement model `CERTIFIED`; SLO values `EMPIRICAL`.

## 1. Purpose

Define what ECHO means by near-real-time and where delay originates. Reporting only neural inference time would be misleading because streaming/window/event confirmation can dominate.

## 2. Latency decomposition

For one detected physical event:

```text
L_total =
  L_camera_buffer
+ L_network_rtsp
+ L_decode_resample
+ L_window_wait
+ L_queue
+ L_inference
+ L_event_confirmation
+ L_publish
+ L_subscriber (outside core where applicable)
```

Each component should be measured or marked `UNOBSERVABLE` rather than silently folded into “AI latency”.

## 3. Reference timestamps

Keep timestamps at critical boundaries:

```text
acoustic_onset_ground_truth   # evaluation only
source/media timestamp
received_at
decoded_at
window_ready_at
inference_started_at
inference_completed_at
candidate_at
confirmed_at
published_at
subscriber_received_at        # integration test
```

Use monotonic clocks for local duration measurement; wall-clock timestamps are for correlation/audit.

## 4. Windowing floor

A model requiring ~0.96 s context cannot necessarily confirm an event at its onset. Overlapping hop reduces update interval, but confirmation logic adds further delay. Therefore the latency target must reflect acoustic context requirements, not promise zero-latency classification.

## 5. Reported percentiles

At minimum:

```text
p50
p95
p99
max during bounded test
sample/event count
```

Mean alone hides stalls.

## 6. Two benchmark modes

### Offline model latency
Measures preprocessing + inference without RTSP and real-time waiting. Useful for comparing models.

### Streaming end-to-end latency
Measures event onset/availability through confirmation/publication. Required for product claims.

Do not mix the two.

## 7. Multi-source latency

Repeat latency tests while increasing replay/source concurrency. A model that is fast with one source but produces queue lag with eight sources has a capacity problem.

Metrics:

```text
queue_lag_ms/source
window_age_at_inference
end_to_end_latency/source
stale_window_drop rate
```

## 8. Network/camera effects

Camera internal buffering can dominate and is hardware-specific. Real camera integration therefore remains an external gate for field latency certification.

## 9. Event Engine trade-off

Stronger temporal confirmation may reduce false alarms while increasing latency. Benchmark thresholds/M-of-N/cooldown must therefore be evaluated jointly on a Pareto surface rather than optimized independently.

## 10. Instrumentation requirement

Tracing/event logs need correlation identifiers:

```text
source_id
stream_generation
window_id
inference_id
candidate_event_id
event_id
```

This allows a slow alert to be traced back to the exact stage.

## 11. Test scenarios

- clean replay one source;
- multiple concurrent replay sources;
- CPU saturation boundary;
- broker temporarily unavailable;
- stream reconnect;
- real camera once available;
- event near window boundary;
- short transient target.

## 12. SLO freeze rule

Final p95/p99 targets are not frozen until MK1 produces empirical distributions on intended hardware and real-camera data. Until then any numeric limit is labeled `TARGET_CANDIDATE`.
