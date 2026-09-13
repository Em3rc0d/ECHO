# Quarry — Datasets

**Status:** `CERTIFIED_FOR_MK1_DATA_DESIGN`  
**Empirical outputs still pending:** exact manifest counts, field recordings and final class balance.

## 1. Purpose

This quarry determines **what data ECHO may learn from and be evaluated on**, under what label mapping, licensing and split rules. The problem is not simply “find audio clips”. A dataset can contain a label that sounds relevant while being unusable because its semantics, license, recording domain, annotation quality or provenance do not match ECHO.

ECHO's fixed promise remains: **detect and classify acoustic events**. Therefore the data layer must represent observable acoustic phenomena, not inferred incidents or social interpretations.

## 2. Questions owned by this quarry

- Which ECHO target classes have enough usable examples to justify MK1?
- Which source labels are semantically equivalent, broader, narrower or ambiguous?
- What rights apply at dataset level and at individual-asset level?
- How large is the domain gap between curated/web audio and security-camera microphones?
- Which confusers must be deliberately collected as hard negatives?
- How do we prevent source/uploader/recording leakage?
- How do we construct an untouched field holdout?
- How do we preserve reproducibility if online assets disappear?

## 3. Dataset landscape

| Source | Evidence / characteristics | Value to ECHO | Primary risk | MK1 role |
|---|---|---|---|---|
| AudioSet | large YouTube-derived ontology and annotations; source of YAMNet/PANNs pretraining | ontology, pretrained representation, label discovery | media availability and source-domain mismatch | reference/pretraining provenance, not blind raw-data pool |
| FSD50K | 51,197 clips, 200 classes, multilabel, Freesound origin | broad environmental events and candidate positives/negatives | per-clip mixed Creative Commons conditions | filtered training pool with asset-level license manifest |
| ESC-50 | 2,000 five-second clips, 50 balanced classes | reproducible benchmark; includes siren and car horn | small size; full set NC; curated clips | academic sanity benchmark, not production proxy |
| UrbanSound8K | urban clips with ten classes | urban negatives and classes such as siren/horn | narrow ontology and curated segments | supplementary benchmark/domain contrast |
| SONYC-UST | real urban sensor network, multilabel annotations | polyphony, real urban background, device/site variation | taxonomy differs from ECHO | robustness and domain methodology |
| DCASE / DESED | SED tasks with weak/strong labels and overlapping events | temporal detection methodology and evaluation design | mostly domestic/task-specific domain | methodology, strong-label experiments where mapping is valid |
| MIMII | machinery normal/anomalous audio with factory noise | non-target industrial hard negatives, domain shift | anomaly task != event classification | robustness/negative research |
| ECHO Field Dataset | recordings from actual deployment hardware/environment | decisive domain evidence | requires authorization and controlled capture | field holdout + later adaptation |

Primary source registry is maintained in `research/DATASET-MATRIX.md` and `MK0/mining-site/WEB-AUDIT-2026-09-13.md`.

## 4. MK1 target mapping policy

The frozen MK1 acoustic targets are:

```text
GLASS_SHATTER
SIREN
FIRE_ALARM
VEHICLE_HORN
TIRE_SQUEAL
```

`BACKGROUND_NO_TARGET` is an evaluation/training state, and `UNKNOWN` is a decision-layer abstention state rather than necessarily a supervised neuron.

Mapping is **semantic**, not string-based. For every source class we must record one of:

```text
EXACT         same observable phenomenon
NARROWER      source label is a subset of ECHO class
BROADER       source label includes phenomena ECHO does not want
AMBIGUOUS     requires manual review or exclusion
NEGATIVE      valid confuser/background
UNUSABLE      license/provenance/quality prevents use
```

Example: a generic `Shatter` label is not automatically equivalent to `GLASS_SHATTER`; selected clips must actually support glass semantics or the ECHO label must remain broader. Likewise a generic `Alarm` cannot automatically become `FIRE_ALARM`.

## 5. Asset admission contract

No audio asset enters a training/evaluation manifest without at least:

```yaml
asset_id: stable internal id
source_dataset: dataset + release/version
origin_uri: original page/resource
source_asset_id: upstream identifier
sha256: content hash
license_id: exact license for this asset
permitted_use: train|validation|test|research_only
original_labels: [...]
echo_labels: [...]
label_mapping_status: EXACT|NARROWER|BROADER|AMBIGUOUS|NEGATIVE
label_provenance: upstream|manual_review|field_annotation
recording_group_id: physical/source grouping key
uploader_or_source_id: when available
site_id: when applicable
device_id: when applicable
split: train|validation|test|field_holdout
```

If an asset lacks license or provenance information, its default state is `QUARANTINED`, not “probably usable”.

## 6. Leakage prevention

Random clip splitting is insufficient when multiple clips originate from the same physical recording, uploader, sensor, session or event. ECHO uses **group-aware splitting**.

Priority grouping keys:

1. original recording / source asset;
2. physical event or capture session;
3. uploader / collection source;
4. site;
5. device/microphone.

No group may span train and test. The field holdout is isolated from all training decisions, including threshold tuning.

Leakage audit must report:

```text
shared source IDs = 0
shared physical recording groups = 0
shared field sessions between train and holdout = 0
near-duplicate fingerprint collisions = investigated
```

## 7. Hard-negative design

A monolithic `OTHER` class is dangerous because it creates an unbounded semantic bucket. ECHO instead builds explicit families of negatives that are likely to trigger the targets:

| Target | Priority confusers |
|---|---|
| GLASS_SHATTER | metal impacts, ceramic break, keys, dishes, dropped objects, construction transients |
| SIREN | tonal alarms, music/synth sweeps, reversing beepers, vehicle electronics |
| FIRE_ALARM | generic beeps, timers, security alarms, electronic chirps |
| VEHICLE_HORN | alarms, whistles, tonal machinery, loud short tones |
| TIRE_SQUEAL | metal squeal, brakes, machinery friction, high-frequency scraping |

General negatives include speech, music, traffic, engines, wind, rain, footsteps, door slams, barking, construction and ordinary ambient silence/noise.

Hard-negative mining becomes iterative in MK1: run the model over long negative recordings, capture high-confidence false positives, review them, add representative examples to the next training cycle while preserving test isolation.

## 8. Domain mismatch model

Web/curated datasets differ from surveillance audio along several axes:

```text
microphone frequency response
AGC / noise suppression
audio codec and bitrate
sample rate
mounting height/orientation
distance
reverberation
wind/weather
continuous background traffic
packet loss/jitter
event overlap
clipping/compression
```

Therefore offline public-dataset accuracy cannot certify field performance. Domain robustness is evaluated through stratified corruption/replay tests and ultimately `ECHO Field Dataset`.

## 9. Field dataset plan

When hardware access is authorized, recordings should cover a matrix rather than a handful of demos:

```text
distance: 5 / 10 / 15 / 20 / 25 m where safe/feasible
noise condition: low / medium / high
orientation: direct / oblique
codec/bitrate: actual camera settings
weather/environment: observed conditions
target positives + matched hard negatives
```

Metadata must include timestamps, device, codec, sample rate, distance, environment and annotation confidence. Continuous audio is not retained by default outside an approved evaluation protocol.

## 10. Data sufficiency is not a fixed clip count

No arbitrary rule such as “100 clips per class means enough” is certified. Sufficiency depends on diversity, independence and error saturation. Before training, report per class:

```text
unique physical/source groups
unique upstream sources/uploaders
hours and event count
license distribution
domain distribution
hard-negative coverage
train/val/test counts
```

A class can have thousands of highly duplicated clips and still be weaker than a smaller but diverse corpus.

## 11. Decisions closed for MK1

- `DECISION`: manifests are asset-level and hash-addressed.
- `DECISION`: splits are group-aware.
- `DECISION`: field holdout is untouched by model/threshold selection.
- `DECISION`: no giant forced `OTHER`; use background + explicit hard negatives + abstention.
- `DECISION`: public datasets are evidence sources, not proxies for real-camera certification.
- `DECISION`: dataset-level license statements never override per-asset conditions.

## 12. Remaining empirical work

- exact number of admitted assets after semantic/license filtering;
- class balance after deduplication;
- actual camera-domain recordings;
- measured domain shift;
- hard-negative mining results.

These are MK1 build/test outputs, not reasons to reopen the data architecture.

## 13. Invalidation conditions

Re-open this quarry if:

- MK1 taxonomy changes materially;
- a dataset/checkpoint license changes or was recorded incorrectly;
- leakage is discovered;
- field data shows a major missing confuser family;
- camera processing creates a domain incompatible with the current preprocessing assumptions.

## 14. Primary references

- AudioSet: https://research.google.com/audioset/
- FSD50K release: https://zenodo.org/records/4060432
- ESC-50: https://github.com/karolpiczak/ESC-50
- UrbanSound8K: https://urbansounddataset.weebly.com/urbansound8k.html
- SONYC-UST: https://zenodo.org/records/3966543
- DCASE: https://dcase.community/
- DCASE 2024 Task 4: https://dcase.community/challenge2024/task-sound-event-detection-with-heterogeneous-training-dataset-and-potentially-missing-labels
