# MK1 Multi-Source Boundary

**Status:** `FROZEN_LOGICAL_CONTRACT / CAPACITY_EMPIRICAL`

## Principle

One-camera PoC is a deployment choice, not an architecture assumption. Every source is isolated by `source_id` and `stream_generation` from ingest through event state.

## Per-source state

Connection/reconnect, audio buffer, window sequence, lag/drop telemetry and EventEngine state are source-scoped. Model workers may be shared, but model work items always carry source identity.

## Scheduler requirement

A single noisy/high-rate source cannot monopolize all pending work. Use bounded per-source contribution and round-robin/weighted-fair scheduling or equivalent. Exact algorithm/worker count is profiled, not frozen.

## Backpressure

Offline replay can block for completeness. Live mode uses bounded buffers/queues and an explicit stale/freshness policy. Never solve overload with unbounded memory.

## Failure isolation

Disconnect/reconnect one source while others continue. A new generation invalidates late work from the old generation. Source failure does not reset model/EventEngine state for unrelated sources.

## Test points

Run 1,2,4,8 replays or until resource saturation; simultaneous events on different sources; one slow/noisy source; one reconnecting source; overload; verify zero cross-source state leakage.

These counts are test points, not support promises.

## Capacity claim

Supported N is the largest measured load satisfying quality/latency/drop/resource constraints with margin over soak duration on declared hardware.

## Invalidation

If shared model runtime cannot safely/concurrently serve work or codecs demand stronger process isolation, implementation topology can change while contract remains.