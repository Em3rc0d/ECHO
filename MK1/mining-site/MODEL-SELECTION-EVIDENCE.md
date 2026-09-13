# MK1 Model Selection Evidence

**Status:** `PENDING_BENCHMARK`

## Purpose

Become the evidence-backed decision record for `EMP-MODEL-001` after A/B/C results exist.

## Required candidate table

For each candidate/version/seed: checkpoint hash, manifest/split hashes, preprocessing, per-class metrics, macro/micro, calibration, streaming false alarms/misses, latency p50/p95/p99, CPU/GPU/RAM, artifact size and notable failure families.

## Selection procedure

1. eliminate scientifically invalid/incomparable runs;
2. apply frozen operational constraints;
3. compare Pareto frontier of target recall, false alarms, macro quality, latency and resources;
4. review representative errors;
5. document winner and reasons challengers lost.

## Deferral

If no candidate satisfies the envelope, do not choose “least bad” without disclosure. Promote extended model/data experiments and keep `EMP-MODEL-001` open.

## Reproducibility

Link result bundles and raw predictions/event logs. External paper scores appear only as context.

## Invalidation

Taxonomy/data/preprocessing/test leakage changes invalidate affected model selection evidence.