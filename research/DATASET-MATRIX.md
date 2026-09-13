# ECHO Dataset Landscape and Admission Matrix

**Status:** `MK0_CERTIFIED_LANDSCAPE / MK1_ASSET_MANIFEST_PENDING`

## 1. Purpose

Evaluate datasets as evidence sources, not simply as downloadable collections. ECHO needs semantically correct target examples, difficult negatives, valid rights/provenance, group-aware splits and a field-domain holdout.

## 2. Dataset matrix

| Dataset | Nature | Useful ECHO role | Major caveat |
|---|---|---|---|
| AudioSet | large YouTube-derived ontology/annotations | pretrained-model provenance, ontology, label discovery | underlying media rights/availability not implied by metadata license |
| FSD50K | 51,197 clips, 200 classes, 108+ h, multilabel | filtered environmental positives/negatives | mixed per-clip licenses require asset-level filtering |
| ESC-50 | 2,000 balanced 5 s environmental clips | academic sanity benchmark | small/curated; full-dataset use restrictions/NC context |
| UrbanSound8K | 8,732 urban clips, 10 classes | urban domain contrast; horn/siren etc. | narrow ontology and curated segments |
| SONYC-UST | real urban sensor network, multilabel | polyphony, site/sensor/domain methodology | taxonomy differs from ECHO |
| DCASE/DESED | task releases with weak/strong SED labels | temporal/event evaluation methods | release/task-specific domain and terms |
| MIMII | industrial normal/anomalous machinery | hard negatives/domain shift | anomaly objective differs from ECHO |
| ECHO Field Dataset | authorized real camera/mic/site | decisive deployment holdout/adaptation | external/privacy gate |

## 3. Frozen MK1 targets

`GLASS_SHATTER`, `SIREN`, `FIRE_ALARM`, `VEHICLE_HORN`, `TIRE_SQUEAL`. `BACKGROUND_NO_TARGET` and hard-negative families supply non-target evidence; `UNKNOWN` is decision-layer abstention.

## 4. Semantic mapping

A source label is classified `EXACT`, `NARROWER`, `BROADER`, `AMBIGUOUS`, `NEGATIVE`, or `UNUSABLE`. Upstream naming alone does not establish equivalence. Generic shatter/alarm/squeal classes require semantic review.

## 5. Licensing

Dataset landing-page terms are insufficient when individual assets differ. For every admitted audio file record source/release ID, upstream asset ID/URI, exact license, permitted use, hash and attribution requirements. Unknown terms -> quarantine.

## 6. Leakage and deduplication

Never random-split related clips across train/test. Group on original recording/event/session/uploader/site/device as available. Audit near duplicates. Keep field holdout out of training, early stopping, calibration and error-driven feature engineering.

## 7. Hard negatives

Target-specific confusers are first-class: metal/ceramic/dishes for glass; beeps/music sweeps/reversing beepers for siren/alarm; whistles/tonal machinery for horn; brakes/metal friction for tire squeal. Long background source-hours are required to evaluate false alarms.

## 8. Domain mismatch

Public web/curated clips differ from surveillance audio in microphone response, AGC/noise reduction, codec/bitrate, distance, mounting, reverberation, weather, background traffic, clipping and packet loss. Public test scores cannot certify field performance.

## 9. Field dataset

When authorized, preserve device/codec/sample-rate, site/source, distance/orientation, noise condition, event onset/offset and annotation quality. Some recordings may be holdout-only based on permission.

## 10. Sufficiency

No fixed clip-count rule. Report independent source/physical groups, duration/events, diversity, license distribution, hard-negative coverage and performance saturation. Thousands of near-duplicate clips may be weaker evidence than fewer independent events.

## 11. Admission schema

See `MK0/quarries/Q-DATASETS.md`; manifests are hash-addressed and versioned. Any asset change creates a new benchmark data identity.

## 12. Invalidation

Taxonomy/terms/leakage corrections or a major field-domain mismatch trigger manifest/mapping reevaluation, not silent dataset patching.

## Primary references

AudioSet official site; FSD50K Zenodo 4060432; ESC-50 official repo; UrbanSound8K official release/site; SONYC-UST Zenodo 3966543; DCASE community task pages; release-specific terms for every selected asset.