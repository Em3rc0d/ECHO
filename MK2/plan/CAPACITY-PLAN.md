# MK2 Capacity Plan

**Status:** `PROTOCOL_SPECIFIED / CAPACITY_NUMBER_PENDING`

## Objective

Determine sustainable source count and headroom for each declared hardware/model/deployment profile while satisfying latency, drop, quality and stability constraints.

## Load dimensions

Source count, window rate/source, model candidate/version, batch/micro-batch policy, codec/decode cost, event rate, broker/store load and telemetry overhead.

## Test pattern

Baseline idle -> 1 source -> step 2/4/8/... until SLO breach -> ramp/spike -> sustained soak near target capacity -> failure injection under load.

## Metrics

Inference throughput; queue lag p50/p95/p99; dropped/stale windows/source; event latency; CPU/GPU/RAM/VRAM; decoder utilization; broker/store latency; thermal/throttling; fairness by source.

## Capacity definition

Supported N is not the crash point. It is the highest sustained load meeting all frozen SLOs with declared safety/headroom over a soak period.

## Profiles

CPU-only and accelerator profiles may have different certified N. A production claim always names model/config/hardware/audio cadence.

## Failure analysis

When a limit is reached, identify decoder, scheduler, model, memory, broker/store or thermal bottleneck before changing architecture.

## Output

Capacity curve, recommended operating N, headroom and scale trigger feeding deployment/release docs.