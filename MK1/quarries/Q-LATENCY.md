# Quarry — Latency

**Status:** `MEASUREMENT_MODEL_CERTIFIED / VALUES_PENDING`

## Purpose

Measure where time is spent and distinguish model inference speed from actual alert freshness.

## Latency decomposition

```text
L_source   capture/device/network buffering
L_decode   demux/decode/resample
L_window   waiting for enough samples/window hop
L_queue    scheduler backlog
L_model    inference
L_event    temporal confirmation requirement
L_publish  broker/client delivery
L_total    acoustic onset -> confirmed/received alert
```

## Timestamps

Preserve media/capture time where trustworthy, receive, window boundaries, inference start/end, event confirmation, publication and subscriber receipt. Use monotonic clocks for local duration measurements and UTC for cross-system records where appropriate.

## Reporting

p50/p95/p99 by component and total, under 1 source and increasing replay source counts. Include queue lag/drop rate and hardware/runtime profile.

## Trade-offs

More overlap/temporal confirmation improves detection stability but adds compute/confirmation delay. Batching may improve throughput but harm per-event latency. Larger jitter buffers improve stream robustness but add delay.

## Field caveat

Replay excludes camera/network buffering; end-to-end field latency cannot close until `EXT-CAMERA-001`.

## Output

Latency budget identifies bottleneck and informs MK2 SLO/capacity design rather than relying on one average number.