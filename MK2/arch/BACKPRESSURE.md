# MK2 Backpressure Architecture

**Status:** `DESIGN_SPECIFIED / PARAMETERS_PENDING LOAD TEST`

## Problem

When ingest/window rate exceeds inference/delivery capacity, an unbounded system converts overload into memory growth and stale alerts. ECHO must degrade explicitly.

## Boundaries

Per-source PCM ring buffer, per-source/pool window queues, inference result/event queues and outbound delivery buffers each have hard capacity and telemetry.

## Live policy candidates

Freshness-aware drop-oldest/stale-expiration is preferred conceptually for live alerts; adaptive sampling/degraded cadence may be considered. Blocking is appropriate for offline benchmark completeness, not live indefinite backlogs.

## Fairness

One source cannot fill all shared pending slots. Enforce source quotas or fair scheduling. Report drops/lag per source.

## Escalation

Before dropping, capacity manager may scale workers within safe resource bounds. Scaling must not create thermal/memory collapse or thundering-herd behavior.

## Observability

Queue fill ratio, oldest age, dropped/stale windows, dispatch delay, worker utilization and source-specific lag drive health alerts.

## Validation

Step/ramp/spike load; noisy-source adversary; worker slowdown; accelerator throttling; soak. Verify bounded memory and known degradation rather than hidden lag.

## Invalidation

Final policy/thresholds freeze from MK2 load evidence and target event duration/recall sensitivity.