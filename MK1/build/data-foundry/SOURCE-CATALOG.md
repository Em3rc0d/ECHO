# MK1 Data Foundry — Source Catalog

**Status:** `SOURCE_LEVEL_EVIDENCE_FROZEN / ASSET_COUNTS_PENDING_EXECUTION`

## 1. Selection principle

A dataset is selected for a specific role. ECHO does not concatenate every available corpus. Sources are evaluated by semantic fit, rights, independence of recording groups, acoustic domain, annotation quality and usefulness for positives or confusers.

## 2. Source matrix

| Source | Release / evidence | ECHO-positive coverage | Domain value | Rights posture | Default Foundry role |
|---|---|---|---|---|---|
| FSD50K | 1.0, Zenodo 4060432 | `Shatter` (BROADER→glass review), `Siren`, `Vehicle horn` | broad environmental/Freesound | dataset CC-BY plus mixed per-clip CC licenses | `release_safe` filtered pool + hard negatives |
| SONYC-UST | v2 family, Zenodo 3966543 | `car-horn`, `siren` | real urban acoustic sensors, multilabel | CC BY 4.0 | `release_safe` urban positives/background/hard negatives |
| SINGA:PURA | v1.0a, Zenodo 5645825 | `Glass breaking`, `Car horn`, `Siren` | strong temporal labels from urban sensors | CC BY-SA 4.0 | `review_required`; temporal/urban evidence |
| ESC-50 | official repository | `Siren`, `Car horn` | small curated sanity set | full ESC-50 CC BY-NC | `research_extended` sanity only |
| UrbanSound8K | official NYU release | `car_horn`, `siren` | field-recorded urban contrast | CC BY-NC 3.0 | `research_extended` contrast only |
| AudioSet | ontology/dataset metadata | ontology contains all five MK1 target concepts | pretraining/ontology reference | metadata/ontology terms do not grant rights to underlying YouTube media | `reference_only` by default |
| ECHO Field | future controlled release | all classes that can be safely/ethically captured | target microphone/camera/site domain | permission-specific | `field_holdout` first, training only by later governed decision |

## 3. FSD50K detail

`FACT/EVIDENCE`: FSD50K contains 51,197 clips and 200 released classes. The companion release table currently reports approximately:

- `Shatter`: 510 audio samples;
- `Siren`: 132;
- `Vehicle horn, car horn, honking`: 183.

`Shatter` is defined as a brittle rigid substance breaking, so it is broader than ECHO `GLASS_SHATTER`; positive admission requires clip-level evidence that glass is actually present. `Siren` and `Vehicle horn` are semantically aligned with ECHO targets.

The FSD50K release table does not expose `Fire alarm` or `Tire squeal` among the final 200 released classes. They therefore cannot be assumed available merely because they exist in the parent AudioSet ontology/Freesound candidate space.

License handling is asset-level. The official release reports CC0, CC-BY, CC-BY-NC and CC Sampling+ clips. The default `release_safe` profile admits only assets whose exact terms are approved by policy; NC/Sampling+ assets are not silently mixed into a release-safe training run.

## 4. SONYC-UST detail

`FACT/EVIDENCE`: SONYC-UST is a multilabel urban-sensor dataset with 23 fine classes grouped into 8 coarse classes. The `alert-signal` group includes `car-horn`, `car-alarm`, `siren`, `reverse-beeper`, and an uncertain alert class. Later v2 releases include train/validation/test splits and verified annotations; the dataset is CC BY 4.0.

ECHO uses:

- `car-horn` -> `VEHICLE_HORN` (`EXACT`);
- `siren` -> `SIREN` (`EXACT`);
- `car-alarm` and `reverse-beeper` -> target-specific hard negatives, not `FIRE_ALARM` or `SIREN` positives.

Sensor identity is retained for leakage/group audits. Existing SONYC split methodology is evidence for sensor/time-aware evaluation; ECHO still records the upstream split and explicitly controls how assets are used in its own manifest.

## 5. SINGA:PURA detail

`FACT/EVIDENCE`: SINGA:PURA v1.0a provides 6,547 strongly-labelled 10-second urban recordings, temporal onset/offset labels and sensor metadata. It extends the SONYC taxonomy with classes including `Glass breaking`, while retaining `Car horn` and `Siren`. License: CC BY-SA 4.0.

Mappings:

- `3-1 Glass breaking` -> `GLASS_SHATTER` (`EXACT`);
- `5-1 Car horn` -> `VEHICLE_HORN` (`EXACT`);
- `5-3 Siren` -> `SIREN` (`EXACT`).

`Friction brake` and generic `Screeching` are useful confusers/coverage evidence but are **not equivalent to `TIRE_SQUEAL`**. ShareAlike implications are reviewed before using this source in a distributable/product training lineage; until then it is `REVIEW_REQUIRED` for the release-safe profile.

## 6. ESC-50 detail

`FACT/EVIDENCE`: 2,000 five-second clips, 50 classes, 40 examples/class. Relevant classes include `Siren` and `Car horn`. The full dataset is CC BY-NC; the smaller ESC-10 subset has different terms but does not solve ECHO target coverage generally.

Use: sanity check, representation/error-analysis comparison under `research_extended`; do not silently use it in a corpus intended to remain free of NC training assets.

## 7. UrbanSound8K detail

`FACT/EVIDENCE`: 8,732 urban excerpts across 10 classes, with predefined folds and metadata linking slices to Freesound recordings. Relevant labels are `car_horn` and `siren`. License: CC BY-NC 3.0.

Use: research-only urban contrast and split-methodology checks. Preserve `fsID`/occurrence grouping; do not reshuffle excerpts as if independent.

## 8. AudioSet detail

The AudioSet ontology contains direct concepts for `Shatter`, `Siren`, `Fire alarm`, `Vehicle horn` and `Tire squeal`, with large annotation counts compared with many smaller corpora. It remains highly useful for taxonomy, pretrained-model provenance and discovering confusers.

However, AudioSet segments are YouTube-derived. ECHO does not equate the ontology/metadata license with a blanket right to download, store or redistribute every underlying media segment. Default Foundry mode is therefore `REFERENCE_ONLY`; an asset-specific acquisition/rights policy would be required before raw-media admission.

## 9. ECHO Field data

Field data is the only source capable of directly characterizing the actual camera/microphone codec, AGC/noise suppression, distance, mounting, environment and network path. It is therefore decisive for field claims, but is gated by authorization/privacy/device access.

Initial field data is held out. Promoting field clips into training creates a new data version and must preserve a separate untouched field evaluation set.

## 10. Coverage gaps and next acquisition targets

### `FIRE_ALARM`

AudioSet gives strong ontology evidence, but the currently selected release-safe corpora do not yet provide a sufficiently clean direct pool. Do not map generic `Alarm`, `Car alarm`, `Buzzer`, timers or arbitrary beeps to `FIRE_ALARM`.

Required path: identify a permissively licensed direct alarm corpus or create controlled/synthetic examples under documented generation parameters, then validate against authorized real alarm recordings before claiming field performance.

### `TIRE_SQUEAL`

AudioSet contains the concept, but FSD50K's final released taxonomy does not provide it as a released class. SINGA:PURA `Friction brake`/`Screeching` remain non-equivalent.

Required path: permissive direct examples or controlled/field capture. These sources must be measured independently from generic brake/friction confusers.

## 11. Source admission rule

A source's presence in this catalog does **not** admit its assets. Asset admission occurs only after provenance/license/hash/mapping/quality/group/split gates. Source facts are versioned in `configs/data_foundry/source_registry.v1.json`.

## Primary evidence URLs

- FSD50K: https://zenodo.org/records/4060432
- FSD50K companion: https://fsannotator.upf.edu/fsd/release/FSD50K/
- SONYC-UST v2: https://zenodo.org/records/3966543
- SINGA:PURA: https://zenodo.org/records/5645825
- ESC-50: https://github.com/karolpiczak/ESC-50
- UrbanSound8K reference: https://serv.cusp.nyu.edu/projects/urbansounddataset/urbansound8k.html
- AudioSet ontology: https://research.google.com/audioset/ontology/