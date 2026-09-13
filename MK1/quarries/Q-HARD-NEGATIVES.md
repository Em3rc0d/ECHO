# Quarry — Hard Negatives

**Status:** `SEED_FAMILIES_DEFINED / ITERATIVE_MINING_PENDING`

## Purpose

Reduce false alarms from non-target sounds that resemble target spectral/temporal patterns. Random background alone is insufficient.

## Seed families

Glass: metal/ceramic/dishes/keys/dropped objects/construction impacts. Siren: synth/music sweeps, security alarms, reversing beepers. Fire alarm: timers, electronic chirps, generic alarms. Horn: whistles, tonal machinery, alarms. Tire squeal: brakes, metal squeal, scraping/friction machinery.

General background includes speech, music, traffic, engines, wind, rain, footsteps, doors, animals and construction.

## Mining loop

1. run candidate model on long target-free streams;
2. collect high-score false positives with asset/window IDs;
3. manually categorize and verify no true target exists;
4. add representative independent examples to a new training manifest version;
5. keep test/field holdout untouched;
6. retrain/re-evaluate and measure false alarms/source-hour change.

## Risks

Over-mining from one site/device can overfit local negatives. Label mistakes can suppress real targets. Reusing test false positives in training contaminates final evaluation.

## Measurement

Report false alarms by target/confuser family, confidence distribution and source-hours. Track whether a negative family causes multiple classes to activate.

## Closure

This quarry never becomes permanently closed in production; MK1 closes the first iteration when false-positive families are understood and integrated without test leakage.