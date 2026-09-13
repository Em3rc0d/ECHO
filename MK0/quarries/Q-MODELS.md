# Quarry — Models

**Status:** `CERTIFIED_BENCHMARK_SET / WINNER_OPEN_EMPIRICAL`

## Decision question

Which representation/model provides the best ECHO operational frontier under common data, taxonomy and hardware constraints?

## Evidence synthesis

YAMNet provides a compact official transfer-learning baseline. PANNs/Cnn14 provides a stronger/larger AudioSet-pretrained CNN challenger. A small log-mel CNN provides a control without pretrained dependency. AST, HTS-AT, PaSST and BEATs represent modern transformer/self-supervised alternatives worth retaining but not forcing into the first experiment.

## Benchmark arms

```text
A1 YAMNet frozen embeddings + linear/small MLP
A2 YAMNet frozen embeddings + tuned head
A3 optional partial fine-tune if justified
B1 PANNs/Cnn14 feature extraction
B2 optional fine-tune
C  compact ECHO log-mel CNN
```

Extended challengers enter only with verified checkpoint/license, reproducible preprocessing and affordable runtime comparison.

## Comparison dimensions

Per-class recall/precision/F1/PR-AUC, macro/micro metrics, calibration, long-stream false alarms/source-hour, misses, p50/p95/p99 latency, throughput, RAM/VRAM, artifact size and sustainable source count.

## Fairness

Same admitted manifest/groups, same taxonomy, equivalent augmentation data regime, validation-only threshold calibration and frozen test/field holdout. Model-specific frontend differences are versioned rather than hidden.

## Risks

Pretraining domain mismatch, overfitting limited field data, checkpoint provenance, runtime complexity, different input durations, and transformer quality gains that may not justify reduced multi-source capacity.

## Decision

A/B/C is frozen. No winner is selected in MK0.

## Validation

MK1 generates result bundles for each arm, multiple seeds where practical, error analysis and Pareto selection after operational constraints are measured.

## Invalidation

Reopen if a candidate cannot legally/reproducibly run, taxonomy changes, or all A/B/C candidates fail the operating envelope.