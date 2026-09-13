# Model Sources — MK0

**Status:** `CERTIFIED_SOURCE_SET / EXTENDABLE`

## Purpose

Record primary sources for candidate acoustic model families and the specific questions each source answers.

## YAMNet

Primary TensorFlow transfer-learning documentation and TensorFlow Models/Hub artifacts establish input/preprocessing expectations, AudioSet class outputs and embedding use. ECHO uses these facts to define baseline A, not to claim best performance.

Questions retained for benchmark: frozen embeddings vs partial fine-tuning, runtime footprint, export/version pinning, field-domain robustness and score calibration.

## PANNs/Cnn14

Original PANNs paper and author repository establish the AudioSet-pretrained CNN family and available representations/tagging/detection variants. ECHO uses Cnn14 as challenger B and measures runtime/quality on the same ECHO splits.

## AST

Original Audio Spectrogram Transformer paper/repository provides a pure transformer baseline for spectrogram classification. Potential quality must be weighed against memory/CPU latency and input-window assumptions.

## HTS-AT / PaSST / BEATs

These are retained as extended candidates because they represent hierarchical transformer, efficient patchout and self-supervised/general representation approaches. They enter a benchmark only after exact code/checkpoint licenses and preprocessing/runtime are pinned.

## Model source checklist

For every model candidate record:

```text
paper/repo/docs
code license
checkpoint origin/license
pretraining corpus
sample rate/input duration
feature frontend
embedding/output shape
export/runtime options
maintenance/version
```

## Decision boundary

External leaderboard metrics are context, not ECHO selection evidence. The model winner is `EMP-MODEL-001` and requires the project benchmark.

## References

Canonical URLs are consolidated in `research/MODEL-MATRIX.md` and `research/REFERENCES.md`; exact checkpoints will enter MK1 model manifests.