# Quarry — Open Set / OOD

**Status:** `MK1_SIMPLE_ABSTENTION_DESIGN_CERTIFIED / ADVANCED_OOD_DEFERRED`

## Problem

The world contains far more sounds than the five targets. A classifier forced to choose one known class creates false positives. `OTHER` is not mathematically equivalent to open-set recognition and cannot enumerate everything.

## MK1 approach

Use independent target probabilities, validation-derived thresholds, explicit background/hard negatives and an `UNKNOWN`/abstain decision when no target has sufficient evidence. Event Engine temporal confirmation further reduces transient false positives.

## Alternatives

- global max-probability threshold: simple but ignores class score distributions;
- per-class thresholds: selected baseline;
- temperature scaling/calibration: useful when probability quality is poor;
- embedding distance/prototypes: promising for known-vs-unknown structure;
- energy/OOD scores: candidate if model architecture supports it;
- dedicated unknown class: usually incomplete because unknown space is unbounded;
- iterative hard-negative mining: operationally valuable and selected.

## Evaluation

Long negative audio, unseen confuser families and field holdout. Measure false alarms/source-hour, score distributions, coverage/abstention rate and target recall lost due to rejection.

## Decision

Do not add complex OOD machinery before baseline abstention and hard-negative performance are measured. Simplicity and explainability matter in MK1.

## Risks

Too-high thresholds suppress targets; too-low thresholds create alert fatigue. Calibration can shift by device/domain, so field validation is mandatory.

## Invalidation

If unknown confusers dominate false alarms after hard-negative iteration, promote advanced OOD/prototype experiments into benchmark scope.