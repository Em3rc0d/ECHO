# MK1 Evaluation Plan

**Status:** `FROZEN_PROTOCOL`

## Offline evaluation

Per class: precision, recall, F1, PR-AUC, support/unique groups and score/error distributions. Aggregate macro/micro metrics complement, never replace, per-class reporting.

## Calibration

Validation-only reliability/Brier/ECE where useful; fit any calibrator on validation. Thresholds are per class and versioned with model/config.

## Streaming evaluation

Replay long annotated/negative streams through full window + EventEngine path. Measure false alarms/source-hour, physical-event misses, confirmation latency, duplicates/event, fragmentation and onset/offset errors if labels exist.

## Runtime

Fixed hardware/runtime after warm-up: inference p50/p95/p99, end-to-end event latency, throughput, CPU/GPU/RAM, queue lag/drops and artifact size.

## Robustness

Noise/SNR, codec/transcode, gain/clipping, reverb and hard-negative families. Field holdout later provides real-device domain evidence.

## Statistical treatment

Report raw counts; bootstrap confidence intervals over independent groups/events where practical; final shortlist uses multiple seeds if compute permits.

## Error review

Review representative false positives/negatives, low-confidence positives, high-confidence false positives, polyphonic failures and domain failures. Assign likely root cause category.

## Promotion

Choose model after operational constraints + Pareto comparison, not one weighted magic score.

## Invalidation

Leakage, test tuning, taxonomy/preprocessing changes or incomparable hardware invalidates affected result bundles.