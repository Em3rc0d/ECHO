# MK1 Data Foundry — Hard-Negative Catalog v1

**Status:** `SEED_CATALOG_FROZEN / MODEL_DRIVEN_MINING_PENDING`

## 1. Purpose

Random background is not sufficient for a low-false-alarm acoustic detector. The Foundry explicitly curates **sounds that are acoustically similar to a target but semantically not that target**.

Hard negatives are tracked by family so false alarms can be diagnosed rather than hidden inside one generic `OTHER` bucket.

## 2. Target-specific seed families

### `GLASS_SHATTER`

Priority confusers:

- ceramic/crockery impacts and breakage;
- dishes/cutlery/chink/clink;
- metal impacts, dropped objects and keys;
- brittle non-glass shatter;
- door/slam/knock/crack transients;
- construction/machinery impacts.

Special rule: FSD50K `Shatter` is not automatically a positive; clips without glass evidence can become valuable hard negatives after review.

### `SIREN`

Priority confusers:

- car alarms;
- reverse beepers;
- generic alarms/buzzers/chimes;
- tonal machinery;
- whistles/foghorn-like tones where present;
- music/synth sweeps and sustained modulated electronic tones.

### `FIRE_ALARM`

Priority confusers:

- generic alarms;
- car alarms;
- alarm clocks/timers;
- doorbells/chimes;
- reverse beepers;
- telephone/ringtone-like alerts;
- smoke/fire-adjacent sounds that are not the alarm signal itself.

No generic alert family is promoted to a fire-alarm positive merely to increase class count.

### `VEHICLE_HORN`

Priority confusers:

- whistles;
- train/foghorn-like signals where present;
- tonal machinery;
- car alarms;
- sirens;
- musical/brass-like sustained tones;
- bicycle/electronic bells.

### `TIRE_SQUEAL`

Priority confusers:

- friction brakes;
- generic screech/squeak;
- metal scraping/squeal;
- machinery friction;
- rail/wheel squeal-like sounds;
- high-frequency synthetic/music tones.

SINGA:PURA `Friction brake` and `Screeching` are valuable negatives/ambiguity probes but not positive `TIRE_SQUEAL` labels.

## 3. General long-form background

False alarms/hour must be measured on target-free or fully annotated continuous audio covering common environments:

```text
speech / crowds
music
general traffic and engines
wind / rain
animals
footsteps / doors
construction / machinery
household/urban ambience
quiet / low-SNR periods
codec/transmission artifacts when field data exists
```

Background can be multi-label context. A clip with a target plus background class is not a negative target example.

## 4. Negative record fields

Each reviewed hard negative records:

```text
asset_id
confuser_family
targets_confused
source_dataset
source_label(s)
review_status
model_score(s) when mined
window/onset-offset
notes
manifest_version
```

## 5. Mining loop

After the first model exists:

```text
long negative replay
  -> capture high target scores
  -> verify no target is present
  -> cluster/categorize confuser
  -> select diverse independent groups
  -> add to a NEW training manifest
  -> preserve old validation/test/field holdout
  -> retrain
  -> compare false alarms/source-hour + target recall
```

A test false positive is evidence, not training material for the same frozen benchmark. Reusing it for training would invalidate that test as independent evidence.

## 6. Sampling policy

Do not overwhelm positives with millions of trivial negatives. Prioritize diversity and challenging families. Keep per-family/source/group statistics so the training sampler can be changed without rewriting ground-truth semantics.

## 7. Closure for MK1

The seed catalog is sufficient to start. The empirical quarry closes its first MK1 iteration when:

- each target has meaningful confuser coverage;
- long negative replay has been run;
- dominant false-positive families are named;
- at least one model-driven mining cycle has been evaluated;
- reductions in false alarms are reported without hidden recall collapse.

The production catalog remains living evidence in MK2 because new sites/devices can introduce new confusers.