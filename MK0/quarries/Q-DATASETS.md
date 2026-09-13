# Quarry — Datasets

**Status:** `CERTIFIED_FOR_MK1_DATA_DESIGN`  
**Empirical outputs pending:** exact admitted counts, class balance and field recordings.

## Purpose

Determine what ECHO may learn from/evaluate on, under which semantics, licenses and split rules. A dataset label that looks relevant may still be unusable due to ambiguity, rights, duplication or domain mismatch.

## Landscape

| Source | ECHO value | Main risk | Role |
|---|---|---|---|
| AudioSet | ontology/pretraining provenance | underlying media availability/rights | reference |
| FSD50K | broad multilabel environmental clips | mixed per-asset licenses | filtered pool |
| ESC-50 | reproducible small benchmark | small/NC/curated | sanity benchmark |
| UrbanSound8K | urban classes/background | narrow curated domain | domain contrast |
| SONYC-UST | real urban sensors/multilabel | taxonomy mismatch | robustness methodology |
| DCASE/DESED | strong/weak SED labels/metrics | task-specific domain/terms | temporal evaluation |
| MIMII | industrial background/anomaly | different objective | negatives/domain shift |
| ECHO Field | actual device/site | authorization required | decisive holdout |

## Frozen taxonomy

`GLASS_SHATTER`, `SIREN`, `FIRE_ALARM`, `VEHICLE_HORN`, `TIRE_SQUEAL`; plus background/no-target and decision-layer unknown.

## Semantic mapping

Every upstream label maps as `EXACT`, `NARROWER`, `BROADER`, `AMBIGUOUS`, `NEGATIVE` or `UNUSABLE`. Generic `Shatter` does not automatically equal glass; generic `Alarm` does not automatically equal fire alarm.

## Asset admission

```yaml
asset_id: ...
source_dataset: ...
origin_uri: ...
source_asset_id: ...
sha256: ...
license_id: ...
permitted_use: ...
original_labels: [...]
echo_labels: [...]
label_mapping_status: ...
label_provenance: ...
recording_group_id: ...
uploader_or_source_id: ...
site_id: ...
device_id: ...
split: ...
```

Missing license/provenance -> `QUARANTINED`.

## Leakage prevention

Group by original recording/event/session/uploader/site/device as applicable. No group spans train and test. Field holdout is excluded from all training and threshold selection. Audit near-duplicate fingerprints.

## Hard negatives

Glass: metal/ceramic/dishes/keys/construction transients. Siren: tonal alarms/music sweeps/beepers. Fire alarm: timers/security beeps/chirps. Horn: whistles/tonal machinery/alarms. Tire squeal: brakes/metal squeal/friction/machinery. Also speech/music/traffic/wind/rain/doors/barks/construction.

## Domain mismatch

Camera microphones introduce frequency response, AGC/noise suppression, codec, distance, mounting/orientation, wind/reverb, clipping and network gaps. Public-dataset accuracy therefore cannot certify field performance.

## Field plan

When authorized: stratify distance, noise, orientation, actual codec/device and matched negatives; preserve metadata and an untouched holdout.

## Sufficiency

No arbitrary clip threshold. Report independent groups, duration/events, source diversity, license distribution, confuser coverage and error saturation.

## Decisions

Asset-level hash/license/provenance; group-aware split; untouched field holdout; explicit negatives; public datasets not field proxies.

## Invalidation

Reopen for taxonomy/license changes, leakage, major missing confuser family or field-domain evidence incompatible with preprocessing.

## Primary references

AudioSet, FSD50K Zenodo, ESC-50, UrbanSound8K, SONYC-UST, DCASE and release-specific terms.