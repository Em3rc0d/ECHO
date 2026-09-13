# MK2 Load and Soak Tests

**Status:** `PROTOCOL_SPECIFIED`

## Load profiles

Step source count, ramp, burst/spike, mixed source rates/codecs and sustained target/background event rates. Use deterministic replay where needed to compare quality under load.

## Soak

Run near intended operating load long enough to expose memory leaks, file descriptor/process growth, broker/store accumulation, thermal throttling and queue drift. Duration becomes profile-specific; it must be long enough to reach steady operational behavior.

## Metrics

Per-source queue lag/drop rate, event latency p95/p99, inference throughput/utilization, RAM/VRAM, decoder CPU, broker/store latency, reconnect/errors, thermal/clock throttling and model/event-quality regressions under load.

## Fairness

A noisy/high-rate source cannot dominate capacity. Report per-source distribution, not just totals.

## Capacity pass

Supported N is below the first unstable/SLO-breaching point with documented headroom. Crash-free operation alone is insufficient.

## Soak failure

Monotonic memory/lag growth, widening tail latency, unfair drops or event-quality degradation triggers root-cause analysis and re-run.

## Evidence

Load generator config/manifest, deployment release, hardware telemetry and result timeline retained.