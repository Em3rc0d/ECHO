# Quarry — Class Mapping

**Status:** `CERTIFIED_FOR_MK1_TAXONOMY_V1`

## 1. Purpose

Translate heterogeneous upstream labels into the stable ECHO taxonomy without semantic drift. A mapping is not valid because two class names look similar; it is valid only when the underlying **observable acoustic phenomenon** is compatible.

Frozen MK1 targets:

```text
GLASS_SHATTER
SIREN
FIRE_ALARM
VEHICLE_HORN
TIRE_SQUEAL
```

Operational non-target states:

```text
BACKGROUND_NO_TARGET
UNKNOWN (decision-layer abstention)
```

## 2. Mapping relation types

Every source label must be assigned one relation:

```text
EXACT
NARROWER_THAN_ECHO
BROADER_THAN_ECHO
OVERLAPS_PARTIALLY
AMBIGUOUS_REQUIRES_REVIEW
NEGATIVE_CONFUSER
UNUSABLE
```

This relation is stored in the asset/class manifest and cannot be inferred later from the label string alone.

## 3. Positive definition and exclusions

### GLASS_SHATTER

Positive: acoustic signature of glass fracturing/shattering.  
Exclude unless manually verified: generic “shatter” involving ceramic, brittle plastic or unspecified material.

Expected confusers: dishes, dropped metal, keys, construction transients, ceramic breakage.

### SIREN

Positive: sustained/modulated siren-like warning acoustic pattern.  
Exclude: generic single electronic beeps and alarms whose acoustic structure belongs to FIRE_ALARM or another narrow class.

Expected confusers: synth/music sweeps, reversing alarms, tonal machinery.

### FIRE_ALARM

Positive: alarm pattern acoustically attributable to a fire/smoke-alarm class in the source annotation or verified clip.  
Exclude: generic alarm labels without evidence that the sound belongs to the fire-alarm acoustic class.

Expected confusers: timers, security alarms, appliance beeps.

### VEHICLE_HORN

Positive: motor-vehicle horn/honking acoustic event.  
Exclude: train horns or other horn instruments unless ECHO deliberately broadens the target in a future taxonomy version.

Expected confusers: whistles, alarms, short tonal machinery.

### TIRE_SQUEAL

Positive: tire-road friction squeal/skid acoustic event.  
Exclude: generic metal squeal, brake squeak or machinery friction unless verified as tire-origin audio.

Expected confusers: metal scraping, brakes, high-frequency mechanical friction.

## 4. Ontology mapping procedure

For each upstream dataset/class:

1. read the official class definition/ontology, not only the display name;
2. inspect label hierarchy and examples where available;
3. identify whether source annotation is weak/strong and single/multilabel;
4. sample-review candidate audio where licensing/access permits;
5. assign mapping relation;
6. record exclusions and confuser behavior;
7. freeze mapping version in the dataset manifest.

## 5. Asset-level override

Dataset-level mapping does not force every clip to the same outcome. Example: an upstream `Shatter` class may be `BROADER_THAN_ECHO`; individual clips manually verified as glass can be admitted to `GLASS_SHATTER`, while ambiguous clips remain excluded/quarantined.

## 6. Multilabel coexistence

The following is allowed conceptually:

```text
SIREN + VEHICLE_HORN
SIREN + TIRE_SQUEAL
FIRE_ALARM + BACKGROUND speech/noise
```

Targets are not mutually exclusive. Mapping/import logic must preserve valid source multilabel annotations rather than collapsing to one label.

## 7. Label quality levels

Recommended provenance grades:

```text
A: strong/manual ECHO-reviewed annotation
B: trusted upstream strong label
C: trusted upstream weak/clip-level label
D: automatically inferred/pseudo-label -> never treated as ground truth without explicit experiment flag
```

Benchmark reports should preserve grade distribution per class.

## 8. Unknown and background

`UNKNOWN` is not a mapping destination for ordinary source clips. Unknown is a runtime abstention state. Non-target labeled data maps to explicit hard-negative families or `BACKGROUND_NO_TARGET` where appropriate.

## 9. Mapping conflicts

If two datasets use the same word with different semantics, ECHO keeps separate source mappings. The ECHO label is the canonical meaning; upstream names never redefine it.

## 10. Validation

Before manifest freeze:

- review random positives per source dataset/class;
- review boundary/ambiguous cases;
- verify no target mapping relies only on string matching;
- document known false-label patterns;
- hash/version the mapping table.

## 11. Invalidation

Re-open if ECHO taxonomy changes, an upstream ontology/release changes materially, manual review finds systematic semantic mismatch, or field errors reveal that a target is too broad/narrow to be operationally useful.

## 12. Upstream evidence

See:

- `MK0/quarries/Q-DATASETS.md`
- `research/DATASET-MATRIX.md`
- AudioSet ontology: https://research.google.com/audioset/ontology/index.html
