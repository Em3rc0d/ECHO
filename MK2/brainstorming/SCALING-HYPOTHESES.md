# MK2 Scaling Hypotheses

**Status:** `OPEN_EMPIRICAL`

## H-SCALE-01 — shared inference workers

A shared bounded worker pool should use accelerator/model memory more efficiently than one full model copy per source. Measure throughput, queue contention and fairness.

## H-SCALE-02 — vertical before distributed

A single host may support the initial target source count; distributed queues/workers are justified only when capacity/resilience evidence requires them.

## H-SCALE-03 — batching trade-off

Cross-source batching may improve throughput but can increase per-event latency. Benchmark batch=1 and bounded micro-batching under identical load.

## H-SCALE-04 — model choice affects topology

The selected model footprint may determine whether CPU-only, single GPU or multiple inference workers are viable. Scale architecture is therefore downstream of MK1 model selection.

## H-SCALE-05 — source ingest is not the only bottleneck

Decode, preprocessing, model inference, EventEngine, broker/storage and observability can each saturate first. Capacity tests measure per-component utilization/lag.

## H-SCALE-06 — bounded degradation

Under overload, dropping stale live windows with explicit health may be safer than processing an ever-growing backlog. Verify effect on event recall.

## Closure

Each hypothesis becomes decision only after capacity/load/soak evidence on a declared hardware/deployment profile.