# Quarry — Thresholds, Calibration and Event Tuning

**Status:** methodology `CERTIFIED`; threshold values `EMPIRICAL`.

## 1. Purpose

Determine how model scores become candidate/confirmed acoustic events without inventing a universal `0.5` threshold.

## 2. Why per-class thresholds

Different targets can have different class prevalence, score calibration, acoustic variability and cost of false positives. Therefore each class may require its own operating point.

Parameters potentially tuned per class:

```text
enter_threshold
exit_threshold
confirmation M-of-N / aggregation rule
min_duration
max_gap
merge_gap
cooldown
```

## 3. Data separation

```text
train -> fit model
validation -> calibration + threshold/Event Engine tuning
frozen test -> unbiased evaluation
field_holdout -> final domain check
```

Never tune thresholds on test/field holdout and then report those same sets as unbiased results.

## 4. Candidate threshold objectives

Possible objectives include:

- maximize F1 on validation;
- satisfy minimum recall then minimize false positives;
- satisfy maximum false alarms/source-hour on streaming validation;
- class-specific operational constraints.

ECHO should prefer explicit constraints over a one-size-fits-all metric.

## 5. Clip threshold vs event threshold

A threshold that maximizes clip/window F1 may produce poor continuous-event behavior. Final tuning must include streaming replay through Event Engine.

## 6. Calibration

Evaluate reliability curves/Brier score and optionally ECE. If post-hoc calibration is used:

```text
fit on validation only
version calibrator
bundle with model artifact
revalidate after model retraining
```

Calibration cannot repair a model that does not separate positives from negatives.

## 7. Hysteresis

Consider separate enter/exit thresholds to avoid event chatter. This interacts with temporal aggregation and must be tuned/evaluated as a profile.

## 8. Search procedure

For each class:

1. generate frozen validation scores;
2. sweep candidate score thresholds;
3. combine with small, predeclared Event Engine parameter grid;
4. compute recall/precision/F1 and streaming FP/hour/latency;
5. reject unstable points across groups/noise strata;
6. choose a candidate operating point from operational constraints;
7. freeze profile before test evaluation.

Avoid massive unconstrained hyperparameter search that overfits the validation set.

## 9. Confidence intervals/stability

Threshold decisions should be checked across independent validation groups and bootstrap intervals where practical. If a threshold changes drastically with small resampling, the model/validation evidence is unstable.

## 10. Threshold profile artifact

```yaml
profile_version: echo.thresholds.v1
model_version: ...
class:
  GLASS_SHATTER:
    enter: ...
    exit: ...
    confirmation: ...
    cooldown_ms: ...
validation_manifest_sha256: ...
selection_rule: ...
```

## 11. Drift

Thresholds are tied to model/preprocessing/domain version. New model, major codec change or meaningful field drift invalidates the assumption that old thresholds remain calibrated.

## 12. Non-negotiable rule

No production-looking threshold value is written into the design as fact before validation evidence exists.
