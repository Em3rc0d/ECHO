# Benchmark Design — MK0

**Status:** `CERTIFIED_PROTOCOL_V1`  
**Purpose:** decide how ECHO will produce its own model evidence before choosing a winner.

## 1. Decision question

Which model/pipeline gives the best operational trade-off for ECHO's target acoustic events under the actual constraints of near-real-time continuous processing?

Published leaderboard scores are background evidence only. They cannot decide the ECHO model because datasets, classes, microphones, thresholds and hardware differ.

## 2. Minimum benchmark arms

### A — YAMNet embeddings + ECHO head

YAMNet is the compact transfer-learning baseline. Official TensorFlow documentation specifies mono 16 kHz input, 0.96 s frames with 0.48 s hop and a 1024-dimensional embedding output.

Experiments:

```text
A1 frozen YAMNet + linear/small MLP head
A2 frozen YAMNet + tuned head capacity
A3 optional partial fine-tuning only if A1/A2 plateau and reproducibility permits
```

### B — PANNs / Cnn14 representation

Use a pretrained PANNs/Cnn14 path under the same ECHO labels/splits. Feature extraction vs fine-tuning must be reported separately because compute and overfitting risk differ.

### C — ECHO compact log-mel CNN

A small model trained for the ECHO taxonomy acts as a scientific control:

- no large pretrained representation dependency;
- easier deployment/export;
- tests whether transfer learning materially helps.

It is not assumed to be weaker or stronger in advance.

### Extended challengers

AST, HTS-AT, PaSST, BEATs/ATST-class models are admitted only when:

- checkpoint/code license is verified;
- preprocessing is reproducible;
- hardware can run a fair benchmark;
- comparison does not consume the project before the core baseline is understood.

## 3. Dataset freeze

Every arm uses the same versioned manifest and group-aware splits.

Required benchmark dataset identity:

```yaml
manifest_sha256: ...
taxonomy_version: echo.taxonomy.v1
train_groups_sha256: ...
validation_groups_sha256: ...
test_groups_sha256: ...
field_holdout_sha256: ...
augmentation_policy_version: ...
```

No model receives extra target-labeled examples unless the experiment is explicitly named as a separate data-regime comparison.

## 4. Split constraints

- same source/physical group never spans train and test;
- field holdout is untouched until final model/threshold selection;
- augmentation only applies to training;
- test data never participates in early stopping, threshold selection or feature engineering;
- near-duplicates are audited.

Suggested 70/15/15 proportions are implementation guidance, not a law. Group integrity takes precedence over exact percentages.

## 5. Training fairness

Record for every run:

```text
code commit
model/checkpoint hash
manifest hash
seed
optimizer/schedule
max epochs
early stopping rule
batch size
class weighting/sampling
augmentations
preprocessing version
hardware + runtime versions
training duration
```

At least multiple seeds should be used for the final shortlist when computationally feasible; one lucky seed must not become the selected architecture.

## 6. Threshold separation

Training model parameters and choosing event thresholds are different tasks.

```text
train -> validation scores -> calibration/threshold selection -> frozen test
```

Per-class thresholds are allowed because score distributions differ by class. A global `0.5` threshold is a baseline, not a certified operational policy.

## 7. Offline metrics

Report per class:

```text
precision
recall
F1
PR-AUC
support / unique groups
confusion or co-activation analysis
```

Report aggregate macro and micro values, but do not hide a failing critical class behind a good average.

For multilabel output use multilabel-appropriate scoring; do not convert the problem to mutually exclusive softmax for convenience.

## 8. Streaming replay metrics

Clip metrics are insufficient for an always-on detector. Replay long continuous audio through the complete window + Event Engine path and report:

```text
false alarms / source-hour
missed physical events / class
detection latency from acoustic onset
alert latency
duplicate confirmed events / physical event
event fragmentation rate
onset/offset error when strong labels exist
```

DCASE/PSDS-style temporal evaluation is useful when strong ground truth exists, but ECHO also keeps direct operational false-alarm and miss measures.

## 9. Runtime benchmark

Run on fixed hardware after warm-up. Separate preprocessing, model inference, Event Engine and publication latency.

Report:

```text
model artifact size
resident RAM / VRAM
CPU/GPU utilization
inference p50/p95/p99
end-to-end p50/p95/p99
windows/s throughput
real-time factor
energy/thermal observations where available
```

Batch=1 is mandatory because live latency matters. Additional batching experiments are allowed for multi-source throughput, but results must not be mixed.

## 10. Robustness matrix

Each finalist is evaluated under controlled transformations that approximate expected field conditions:

```text
SNR/noise strata
codec/transcode conditions
sample-rate normalization
gain/clipping
reverberation
packet-gap simulation where meaningful
hard-negative families
```

The goal is not to make synthetic noise look realistic by assumption; it is to identify sensitivity before field testing.

## 11. Calibration

Evaluate probability usefulness with Brier score/reliability curves and optionally ECE. Calibration is important because Event Engine thresholds and severity policy consume scores.

If temperature scaling or another post-hoc calibrator is used, fit it only on validation data and version it as part of the model artifact.

## 12. Selection rule: constraints then Pareto

ECHO does **not** define an arbitrary weighted score such as `0.4 F1 + 0.3 latency ...`. Selection occurs in two steps:

1. eliminate candidates that violate operational constraints once those constraints are measured/frozen;
2. compare remaining candidates on the Pareto frontier of critical recall, false alarms, macro F1, latency and resources.

A slightly more accurate model may lose if it cannot sustain the required source count or generates more false alerts in long replay.

## 13. Statistical reporting

Where possible:

- bootstrap confidence intervals over independent groups/events;
- multiple seeds for model training;
- error bars for latency/load tests;
- report raw counts alongside ratios;
- preserve per-class result tables.

Claims such as “B beats A” require a reproducible difference, not just one decimal point from one run.

## 14. Error analysis gate

Before selecting a winner, manually review representative:

```text
false positives by class
false negatives by class
low-confidence true positives
high-confidence false positives
simultaneous-event failures
field/domain failures
```

Each failure is assigned a likely category: data, label ambiguity, representation, threshold, Event Engine, audio quality or domain shift. This avoids trying to repair every issue by changing the neural network.

## 15. Reproducible result bundle

Every benchmark candidate outputs:

```text
run manifest
model/checkpoint hash
config
metrics.json
per-class metrics
predictions on frozen test
streaming event log
latency/resource measurements
calibration artifacts
error-analysis notes
```

Result bundles become certification evidence for the model decision.

## 16. Stop conditions

The minimum A/B/C benchmark is complete when all candidates have comparable result bundles and no known leakage invalidates the test. Extended transformers are not required if the minimum set already yields a model that satisfies the operational envelope.

## 17. Invalid benchmark conditions

Invalidate and rerun affected comparisons when:

- taxonomy changes;
- split leakage is discovered;
- one model used different data without explicit experiment labeling;
- thresholds were tuned on test;
- hardware/runtime changed for a latency comparison;
- preprocessing differs unintentionally;
- corrupted/mislabeled assets materially affect results.

## 18. Primary evidence

- YAMNet transfer learning: https://www.tensorflow.org/tutorials/audio/transfer_learning_audio
- PANNs paper/repo references: `research/MODEL-MATRIX.md`
- DCASE 2024 SED methodology: https://dcase.community/challenge2024/task-sound-event-detection-with-heterogeneous-training-dataset-and-potentially-missing-labels
- ECHO dataset policy: `MK0/quarries/Q-DATASETS.md`

No winner is certified in MK0. The benchmark protocol is certified; the winner is an MK1 experimental output.
