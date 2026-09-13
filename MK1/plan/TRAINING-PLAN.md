# MK1 Training Plan

**Status:** `PROTOCOL_READY`

## Common controls

Same taxonomy, split groups and admitted data regime for A/B/C. Training-only augmentation. Fixed/recorded seeds, optimizer/schedule, early stopping, class weighting/sampling and dependency versions.

## A — YAMNet

Start frozen embeddings + small head; vary head capacity as a named experiment. Partial fine-tuning only if frozen baseline plateaus and resources/data justify it.

## B — PANNs/Cnn14

Evaluate feature extraction first; optional fine-tune as separate experiment. Record frontend/window assumptions and runtime footprint.

## C — compact CNN

Use a versioned log-mel frontend and architecture small enough to serve as deployment/scientific control. Do not artificially disadvantage it with fewer tuning opportunities.

## Loss/outputs

Multi-label targets use sigmoid-compatible multilabel loss/metrics. Class imbalance strategy is explicit and does not alter test distribution.

## Augmentation

Candidate noise mixing, gain, reverb and codec-like transforms are train-only and versioned. Ablate their value on validation/holdout rather than assuming benefit.

## Checkpointing

Every retained checkpoint has model ID, code commit, config, seed, manifest hash and checkpoint hash.

## Stop conditions

Divergence, leakage, non-reproducibility or license ambiguity blocks promotion. Overfitting is handled by data/error analysis rather than repeatedly inspecting test results.

## Output

Comparable checkpoints/result metadata for evaluation plan.