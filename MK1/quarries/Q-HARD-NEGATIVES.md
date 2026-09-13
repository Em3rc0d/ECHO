# Quarry — Hard Negatives

**Status:** strategy `CERTIFIED`; mined corpus `ITERATIVE_MK1_OUTPUT`.

## 1. Purpose

Reduce operational false alarms by explicitly training/evaluating sounds that resemble ECHO targets. Generic background alone is insufficient because most field errors are expected to concentrate in acoustically similar events.

## 2. Taxonomy of negatives

Use three layers:

```text
ambient negatives    common background with no target
semantic confusers   known event classes acoustically close to targets
mined negatives      real high-scoring false positives discovered by ECHO
```

Mined negatives are the most valuable after the first model exists, but they must never contaminate the frozen test/field holdout.

## 3. Initial confuser matrix

| Target | High-priority negatives |
|---|---|
| GLASS_SHATTER | dishes, ceramic break, dropped metal, keys, construction impacts, door slam |
| SIREN | electronic alarms, reversing beeper, tonal music/synth, whistles, machinery tones |
| FIRE_ALARM | timers, appliance beeps, security alarms, reversing alarms, short electronic chirps |
| VEHICLE_HORN | whistles, sirens, alarms, musical horns, tonal machinery |
| TIRE_SQUEAL | metal squeal, brakes, scraping, machinery friction, construction tools |

General ambient negatives: speech, music, traffic, engines, wind, rain, footsteps, animals, HVAC, quiet room/outdoor ambience.

## 4. Mining loop

```text
model_vN
 -> replay long negative corpus
 -> collect high-score non-target windows/events
 -> human/ground-truth review
 -> classify failure family
 -> add eligible examples to training pool
 -> keep frozen validation/test untouched
 -> train model_vN+1
```

Every mined asset keeps the model version that discovered it. This makes later analysis possible: which failures stopped recurring and which persisted?

## 5. False-positive review record

Recommended schema:

```yaml
fp_id: ...
source_asset_id: ...
source_id/site: ...
model_version: ...
predicted_class: ...
peak_score: ...
actual_family: metal_impact|speech|alarm|...
review_status: confirmed_negative|ambiguous|annotation_error
notes: ...
```

## 6. Sampling strategy

Do not add only the top 100 highest-scoring negatives. That can overfit to a tiny failure mode. Sample across:

- score bands;
- sources/sites;
- devices/codecs;
- negative families;
- time periods/noise conditions.

## 7. Class imbalance

Hard-negative quantity should not blindly overwhelm positives. Compare weighting, balanced batches or targeted sampling. Record the policy per experiment.

## 8. Ambiguous examples

If a clip could plausibly contain the target, it is not a safe negative. Mark `AMBIGUOUS` and remove from hard-negative training until reviewed. Incorrect negatives can teach the model to suppress true events.

## 9. Evaluation

Track:

```text
FP/source-hour overall
FP/source-hour by target
FP count by confuser family
score distribution shift after mining
recall impact on true positives
```

A reduction in false alarms that causes unacceptable recall loss is not success.

## 10. Leakage guard

Assets mined from field holdout/test are **analysis evidence only** for the current evaluation cycle. They may enter a future training generation only after a new holdout is established and versioned.

## 11. Closure rule

The strategy is closed. Hard-negative mining remains a continuing model-improvement process through MK1/MK2; no finite list can be declared universally complete.
