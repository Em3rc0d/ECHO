# Non-Functional Drivers — MK0

**Status:** `CERTIFIED_DRIVERS / NUMERIC SLOS EMPIRICAL`

## Purpose

Define qualities that shape architecture before numeric SLOs exist. Values such as p95 latency or source capacity remain `TARGET/EMPIRICAL` until MK1 measurements.

## Drivers

### Correctness and scientific validity

Per-class behavior, group-aware splits, reproducible preprocessing and frozen test data are higher priority than a single aggregate accuracy number. Leakage or test tuning is a critical failure.

### Low false-alarm burden

Always-on detection means false alarms/source-hour is a core product metric. Hard negatives and long negative replay are mandatory.

### Near-real-time freshness

Live queues must be bounded. Under overload, the system must expose lag/drops rather than accumulate hours of stale audio.

### Multi-source isolation

One source cannot corrupt another source's Event Engine state, timestamps, buffer or health. Failures are isolated by source.

### Reproducibility

Results reference code commit, dataset manifest hash, model/checkpoint hash, config and runtime/hardware profile.

### Observability

Source connection, decode health, queue lag, dropped windows, inference latency, event counts and broker delivery state must be observable without logging sensitive audio/credentials.

### Privacy/security

Continuous audio retention, ASR and speaker identification are disabled by default. Secrets remain external to Git. Media capture for evaluation requires explicit authorization.

### Portability/replaceability

Source adapters, model runner and publisher are contracts. FFmpeg, model backbone or broker can be replaced without rewriting event semantics.

### Resource efficiency

The product should be feasible on modest local hardware for PoC; CPU/GPU/RAM limits are measured, not assumed.

## Trade-offs

Higher temporal confirmation can reduce false positives but increase detection latency/misses for short events. Larger models may improve quality but reduce sustainable source count. More buffering tolerates jitter but increases latency. These are benchmark dimensions, not hidden implementation choices.

## Validation

Each driver maps to MK1/MK2 tests: model benchmark, streaming replay, load/soak, fault injection, privacy/security checks and reproducibility bundles.

## Invalidation

If deployment priorities change—for example hard real-time requirements or mandatory cloud inference—revisit the ranking and architecture.