# Quarry — Data / Model Drift

**Status:** `MONITORING_DESIGN_READY`

## Drift types

Source/device replacement or firmware/AGC changes; new seasonal/weather/background sound; site construction/traffic changes; new confuser class; event prevalence shift; model/config release interaction.

## Signals

Target score distributions, confirmed-event rate, high-confidence unknown/negative activations, source signal statistics, false-positive review, field-labeled sample performance and device/config metadata changes.

## Caution

Unlabeled score drift does not automatically prove quality degradation. It is a trigger for review/sampling, not an automatic retraining command.

## Response

Collect authorized representative evidence -> label/review -> compare active model on regression/field set -> decide threshold/config adjustment or new training version -> full regression -> controlled release.

## No online self-training requirement

MK2 does not require the production model to learn automatically from its own outputs, which risks feedback loops and silent corruption.

## Governance

New data enters a versioned manifest with provenance/permission; historical holdout remains protected.

## Invalidation

Monitoring features evolve when field evidence reveals better drift indicators.