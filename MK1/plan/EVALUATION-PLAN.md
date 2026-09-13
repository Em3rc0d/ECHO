# Evaluation Plan — MK1

## Tres capas

### 1. Clip/window ML
Precision, recall, F1 por clase, macro-F1, PR curves, calibration.

### 2. Event-level
Matching temporal entre ground truth y confirmed events; false alarms/hour, misses, duplicates/event, onset delay.

### 3. System-level
Capture-to-publish latency p50/p95/p99, real-time factor, CPU/RAM, recovery time y backlog.

## Slices obligatorios

clean/noisy, near/far si existe field data, codec/source type, class, hard negatives y long-background audio.

## Holdout discipline

El field test final no se usa para ajustar thresholds. Si se usa para tuning, debe crearse un segundo holdout.