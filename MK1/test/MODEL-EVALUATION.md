# MK1 Model Evaluation

**Status:** `PROTOCOL_READY / RESULTS_PENDING`

## Compared candidates

A YAMNet+head, B PANNs/Cnn14+head, C compact log-mel CNN under common data groups/taxonomy. Additional candidates are separate named experiments.

## Offline reports

Per-class precision/recall/F1/PR-AUC/support, macro/micro summaries, calibration plots/Brier/ECE where useful, prediction tables and representative error examples.

## Streaming reports

Use complete model+EventEngine. Report false alarms/source-hour, misses/physical-event recall, detection latency, duplicates/event and fragmentation. A model with better clip F1 may lose due to continuous false alarms or runtime.

## Runtime

Fixed hardware/runtime, warm-up, batch=1 and optional multi-source batch test. p50/p95/p99, throughput, CPU/GPU/RAM and artifact size.

## Selection

Apply operational constraints first, then Pareto comparison. Avoid arbitrary weighted sum. Document why winner is selected and what class/failure weaknesses remain.

## Statistical care

Raw counts, independent group bootstrap where feasible and multiple training seeds for finalists when resources permit.

## Invalidation

Leakage, test tuning, preprocessing/data mismatch or incomparable hardware invalidates affected comparison.