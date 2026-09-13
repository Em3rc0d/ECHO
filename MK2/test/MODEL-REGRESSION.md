# MK2 Model Regression

**Status:** `PROTOCOL_SPECIFIED`

## Reference sets

Frozen public-domain/regression subsets, hard-negative suites, long negative streams, annotated target streams and authorized field holdout stratified by known conditions.

## Comparison

Candidate vs active model under same preprocessing/runtime/event protocol where compatible. Report per-class recall/precision/F1/PR-AUC, false alarms/source-hour, misses, calibration, latency/resources and changed failure families.

## Critical-class rule

An aggregate improvement cannot hide a material regression in one critical target. Promotion policy defines acceptable per-class non-inferiority/improvement bounds before final test.

## Domain slices

Device/site/noise/distance/codec slices where sufficient data exists. Avoid drawing statistical conclusions from tiny slices; report raw counts and uncertainty.

## Event-level evaluation

Compare complete EventEngine output, not only window scores, because threshold/calibration changes may alter operational behavior.

## Drift relationship

Observed production drift can add a new regression slice in the next version, but historical holdout/test assets are not contaminated by retraining without a versioned policy.

## Output

Regression certificate input for model promotion/rollback decision.