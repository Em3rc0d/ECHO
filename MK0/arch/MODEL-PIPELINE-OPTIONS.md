# Model Pipeline Options — MK0

**Status:** `BENCHMARK_SET_CERTIFIED / WINNER_EMPIRICAL`

## 1. Decision problem

Choose a representation/classifier path that balances ECHO target quality, long-stream false alarms, latency, memory/CPU/GPU cost, export/deployment friction and reproducibility.

## 2. Minimum candidates

### A — YAMNet + ECHO head

Official TensorFlow material provides a compact AudioSet-pretrained representation with 16 kHz mono input and 1024-dimensional embeddings. ECHO treats it as a baseline representation, not as its final taxonomy.

### B — PANNs/Cnn14 + ECHO head

AudioSet-pretrained CNN representation with strong tagging heritage. Expected trade-off is potentially stronger representation at larger runtime footprint; this must be measured on identical ECHO data/hardware.

### C — compact ECHO log-mel CNN

A from-scratch/control model tests whether pretrained backbones actually add value for the narrow v1 taxonomy and provides a simpler deployment reference.

### Extended candidates

AST, HTS-AT, PaSST and BEATs remain candidates if the A/B/C frontier is insufficient or MK2 resources justify extended comparison.

## 3. Common contract

Every candidate must produce independent target scores for the same taxonomy plus model/preprocessing version. A model-specific feature format must not leak into Event Engine or Pub/Sub contracts.

## 4. Preprocessing fairness

Model-required preprocessing can differ, but the underlying admitted audio and group splits remain identical. All transformations are versioned; test data never influences training/thresholds.

## 5. Runtime modes

Offline benchmark favors completeness/reproducibility; live inference favors bounded latency. Batch=1 latency is required; multi-source batching may be separately tested for throughput.

## 6. Selection dimensions

Per-class recall/F1/PR-AUC, macro/micro metrics, false alarms/source-hour, misses, calibration, inference/end-to-end p50/p95/p99, throughput, RAM/VRAM, model size and sustainable source count.

## 7. Non-decision

MK0 does not choose the model winner. Doing so from published paper results would violate ECHO's benchmark policy because taxonomy/domain/hardware differ.

## 8. Risks

Pretraining domain shift, checkpoint/license ambiguity, hidden preprocessing differences, test leakage, overfitting small field data and model size reducing multi-source capacity.

## 9. Invalidation

Reopen benchmark candidates if no A/B/C option satisfies the measured operating envelope or a licensing/runtime problem makes a candidate unusable.