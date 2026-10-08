# Quarry — Hard Negatives

**Status:** `FIELD_DEMO_CONFUSERS_OBSERVED / ITERATIVE_MINING_OPEN`

## Purpose

Reduce false alarms from non-target sounds that resemble target spectral/temporal patterns. Random background alone is insufficient.

## Seed families

Glass: metal/ceramic/dishes/keys/dropped objects/construction impacts. Siren: synth/music sweeps, security alarms, reversing beepers. Fire alarm: timers, electronic chirps, generic alarms. Horn: whistles, tonal machinery, alarms. Tire squeal: brakes, metal squeal, scraping/friction machinery.

General background includes speech, music, traffic, engines, wind, rain, footsteps, doors, animals and construction.

## 2026-10-08 field-demo trigger

Ad hoc microphone/WAV testing reported two target-free failure modes: ambient-only audio activating GLASS_SHATTER/SIREN and voice-only audio activating GLASS_SHATTER. The raw clips are not governed or committed, so these observations identify a quarry direction but are not benchmark evidence.

A separate short-clip artifact was also identified: repeated zero-padded tail windows could create pseudo-repeated temporal evidence. External demo audio now disables tail padding and requires at least one full analysis window. The long ambient false-positive problem remains open.

See `MK1/test/FIELD-AUDIO-ROBUSTNESS-GATE.md` and issue #53.

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