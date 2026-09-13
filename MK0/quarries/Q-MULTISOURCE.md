# Quarry — Multi-Source Runtime

**Status:** `CERTIFIED_FOR_ARCHITECTURE`  
**Capacity values:** `EMPIRICAL / MK2`

## 1. Purpose

ECHO must not be architected as “a script connected to one camera”. The first PoC may use one physical source, but source identity, buffering, health, event state and scheduling must be independent per source from the first build.

This quarry owns the concurrency and backpressure model required to scale from:

```text
1 replay -> 1 real camera -> N concurrent sources
```

without rewriting the inference/event contracts.

## 2. Core invariants

Each source has independent state:

```text
source_id
connection state
stream generation/session id
audio clock
bounded decode buffer
window sequence
last inference timestamp
Event Engine state per event class
reconnect/backoff state
health metrics
```

No classifier/event-engine state may be shared implicitly between cameras. A glass event on `CAM-01` must never advance confirmation state for `CAM-02`.

## 3. Candidate concurrency models

| Model | Advantages | Failure/complexity | Position |
|---|---|---|---|
| one OS process per source | strong isolation, simple failure boundary | memory/process overhead; model duplication unless separate inference service | useful adapter option, not default assumption |
| async task per source + local inference | simple for few streams | one slow inference can starve event loop if not isolated | acceptable only with executor boundary |
| source tasks + shared bounded inference queue + worker pool | controlled concurrency, model reuse, measurable backpressure | scheduling/fairness required | **MK1/MK2 reference model** |
| external distributed queue + inference workers | horizontal scale and isolation | operational complexity | MK2 scale option after evidence |

The architecture freezes **interfaces**, not an arbitrary number of workers.

## 4. Reference dataflow

```text
SourceSupervisor(source_id)
        |
        v
RTSP/file decoder
        |
        v
bounded PCM ring buffer
        |
        v
WindowProducer
        |
        v
bounded inference scheduler
        |
   +----+----+
   | workers |
   +----+----+
        |
        v
RAW_INFERENCE(source_id, window_id)
        |
        v
EventEngine[state keyed by source_id + event_type]
        |
        v
CONFIRMED_EVENT
```

`source_id` is mandatory through every layer; never reconstruct it from process name/topic position later.

## 5. Buffering rule

Buffers MUST be bounded. Unbounded buffering converts transient overload into increasing RAM and stale alerts.

For live event detection, freshness normally matters more than processing every historical window. Therefore overload behavior is explicit and measurable.

Candidate policy hierarchy:

1. keep a small per-source PCM ring buffer;
2. enqueue windows with capture timestamp and deadline;
3. reject/skip stale windows when their usefulness deadline expires;
4. increment dropped/stale-window metrics;
5. never silently grow memory.

Exact buffer seconds and deadlines are `TARGET_CANDIDATE` until latency/load tests.

## 6. Backpressure choices

| Strategy | When useful | Risk |
|---|---|---|
| block producer | offline/replay where completeness matters | live stream latency grows without bound |
| drop oldest | live detection where newest context matters | may miss event onset under sustained overload |
| drop newest | preserves queued chronology | system remains permanently behind during overload |
| sample/degrade cadence | controlled survival mode | reduced recall for short events |
| scale worker pool | when compute exists | can amplify contention/thermal pressure |

MK1 live policy is **bounded + freshness-aware**, while offline benchmark mode may use blocking/no-drop semantics so model evaluation is deterministic.

## 7. Fairness between sources

A single noisy or high-rate source cannot monopolize inference. Scheduler requirements:

```text
bounded queue contribution per source
round-robin or weighted-fair dispatch
per-source lag metric
per-source dropped-window counter
no single source can occupy all pending slots
```

Priority scheduling by severity is intentionally not performed before inference because severity is not known yet. Operational priority may later be configured by site/source, but must not starve ordinary sources silently.

## 8. Failure isolation

Source lifecycle:

```text
DISABLED
  -> CONNECTING
  -> ONLINE
  -> DEGRADED
  -> RECONNECTING
  -> ONLINE
  -> OFFLINE (after policy exhaustion / operator action)
```

Failure of one source must not terminate the inference workers or other source supervisors.

Each reconnect creates or increments a `stream_generation` so windows from an old session can be rejected if they arrive late.

## 9. Source health model

Minimum telemetry per source:

```text
connection_state
last_audio_packet_at
last_decoded_sample_at
last_window_at
last_inference_at
buffer_fill_ratio
queue_lag_ms
dropped_windows_total
reconnects_total
decode_errors_total
audio_rms/dBFS summary (optional telemetry)
```

Health is different from event detection. An `ONLINE` source with permanently silent/muted audio can be technically connected but acoustically unusable; this needs a separate signal-quality warning.

## 10. Clock and ordering

Every window carries:

```text
source_id
stream_generation
window_seq
captured_at / media timestamp when trustworthy
received_at
window_start_offset
window_end_offset
```

Ordering is enforced per source, not globally across all cameras. Cross-camera clock synchronization is not required for MK1 classification, but becomes relevant if future downstream consumers correlate events across sources.

## 11. PoC validation

One physical camera validates real ingest only. Multi-source abstraction must also be tested with N deterministic replay sources on the same runtime.

Minimum tests before claiming the architecture is multi-source:

- 1, 2, 4, 8 replay sources or until hardware saturation;
- one source disconnect/reconnect while others continue;
- one deliberately slow/noisy source;
- simultaneous target events on different source IDs;
- overload causing bounded drops rather than unbounded memory;
- verify zero state leakage between sources.

The numbers above are **test points**, not supported-capacity claims.

## 12. Capacity model

For each hardware/model configuration measure:

```text
N sources
window rate/source
inference windows/s
CPU/GPU utilization
RAM
queue lag p50/p95/p99
drop rate/source
end-to-end event latency p50/p95/p99
thermal behavior over soak period
```

Supported `N` is the largest load satisfying the final SLOs with margin; it is never inferred from one short benchmark.

## 13. Decisions closed

- `DECISION`: ECHO is logically multi-source from MK1.
- `DECISION`: state is keyed by source.
- `DECISION`: queues and buffers are bounded.
- `DECISION`: live overload is explicit and observable.
- `DECISION`: source failures are isolated.
- `DECISION`: physical multi-camera capacity is not promised before load/soak evidence.

## 14. Open empirical nodes

- worker count and concurrency implementation after profiling;
- queue/buffer sizes;
- maximum sustainable N on target hardware;
- CPU vs GPU deployment economics;
- whether an external queue is justified in MK2.

## 15. Invalidation conditions

Revisit this architecture if the selected model cannot be shared safely between workers, if camera codecs require process-level isolation, if latency tests show freshness-aware dropping is unacceptable for target events, or if MK2 demands distributed inference across hosts.

## 16. Related operational evidence

Frigate demonstrates per-camera audio roles and per-camera MQTT/health surfaces in a production-oriented open-source NVR architecture: https://docs.frigate.video/configuration/audio_detectors/ and https://docs.frigate.video/integrations/mqtt/ . ECHO does not copy Frigate's runtime; it uses it as evidence that camera-scoped audio processing/health/event semantics are operationally viable.
