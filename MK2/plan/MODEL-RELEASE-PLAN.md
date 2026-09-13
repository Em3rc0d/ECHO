# MK2 Model Release Plan

**Status:** `SPECIFIED`

## Candidate package

Model/checkpoint, architecture/runtime compatibility, preprocessing, taxonomy, calibrator, per-class thresholds/EventEngine config, data/training manifest references, benchmark/regression reports, license/provenance and known limitations.

## Promotion

Experimental -> candidate after reproducible training -> staging after full offline/streaming regression -> certified after field/profile/SLO review -> active after controlled rollout.

## Comparison

New model is compared against current active model on identical frozen regression/field suites. Report per-class gains/losses, false alarms, latency/resources and changed failure families.

## Canary

Where deployment permits, run shadow/canary on a limited source subset without automatically acting on new-model alerts until evidence is sufficient.

## Rollback

Keep previous model + compatible calibration/EventEngine config. Rollback trigger includes quality/runtime regression, abnormal false-alert spike or compatibility error.

## Data lineage

Training corpus/version and excluded/holdout sets are linked; production events used for future training enter only through governed review.

## Invalidation

Taxonomy or preprocessing major change creates a new compatibility line rather than an in-place model update.