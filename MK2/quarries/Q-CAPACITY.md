# Quarry — Capacity

**Status:** `PROTOCOL_READY / NUMBERS OPEN`

## Question

How many concurrent sources can a declared ECHO model/hardware/deployment profile sustain while meeting latency, quality, fairness and bounded-resource SLOs?

## Variables

Model/frontend, source cadence/window overlap, codecs/decoder CPU, batch/microbatch, worker count, accelerator, broker/store load, telemetry and target/background event rate.

## Measurement

Step/ramp/spike/soak; p95/p99 queue/event latency; drop/stale rate per source; throughput; CPU/GPU/RAM/VRAM; thermal; fairness; event-quality regression under load.

## Definition

Capacity is the highest load that remains inside **all** frozen constraints with margin over soak. The crash/OOM point is not capacity.

## Scale decision

When SLO breaks, identify bottleneck before adding processes/hosts. A larger model may lose to a slightly weaker model if it materially reduces required source capacity.

## Evidence output

Capacity curves by profile, recommended operating envelope, headroom and bottleneck analysis.

## Invalidation

Model, hardware, window cadence, topology or significant runtime version changes require remeasurement.