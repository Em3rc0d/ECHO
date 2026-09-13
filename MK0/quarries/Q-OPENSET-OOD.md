# Quarry — Open Set, Unknowns and Abstention

**Status:** simple abstention architecture `CERTIFIED_FOR_MK1`; advanced OOD method `OPTIONAL_RESEARCH`.

## 1. Problem

The world contains far more sounds than ECHO target classes. A closed classifier can be forced to assign confidence to something it has never seen. `OTHER` does not solve this mathematically because no finite class can represent every non-target distribution.

## 2. Operational concepts

Separate:

- `BACKGROUND_NO_TARGET`: known/collected non-target audio used during training/evaluation;
- `HARD_NEGATIVE`: non-target sound specifically likely to be confused with a target;
- `UNKNOWN`: decision-layer abstention when no target has sufficient evidence;
- `OOD`: distribution materially different from training data, whether or not detectable automatically.

## 3. MK1 policy

Use explainable mechanisms first:

```text
per-class thresholding
calibration on validation
hard-negative training/mining
Event Engine temporal confirmation
abstain when no class satisfies evidence rule
```

This is preferred over adding a complex OOD detector before ordinary false positives are understood.

## 4. Candidate advanced methods

Research options if MK1 evidence requires them:

- max-probability/score rejection;
- energy-based rejection;
- embedding-distance or prototype methods;
- one-class density estimates;
- dedicated outlier-exposure datasets;
- conformal/selective prediction approaches where assumptions fit.

None is frozen as required.

## 5. Calibration interaction

A poorly calibrated model can appear confident on OOD examples. Calibration must be evaluated separately from discrimination. Per-class reliability matters because different targets can have different score scales.

## 6. OOD evaluation corpus

Create categories outside the five targets, including unseen confuser families and field background. The strongest evaluation set should contain examples never used in hard-negative mining.

## 7. Metrics

Operational metrics remain primary:

```text
false alarms/source-hour on unknown/background streams
selective risk vs coverage
per-class false positive rate on OOD families
score distributions for target vs hard-negative vs unknown
```

AUROC for an OOD detector can be reported if one exists, but it cannot replace event false-alarm metrics.

## 8. Failure modes

- thresholds too low -> alert flood;
- thresholds too high -> missed targets;
- “unknown” becomes a dumping label with no semantics;
- hard negatives leak into test after mining;
- OOD benchmark becomes easier than real ambient audio;
- calibration fitted on test data.

## 9. Closure

MK1 does not require solving open-set recognition in the research sense. It requires a conservative, measured abstention policy and a process to mine/learn from false positives. Advanced OOD becomes justified only if evidence shows ordinary threshold/calibration/hard-negative controls are insufficient.
