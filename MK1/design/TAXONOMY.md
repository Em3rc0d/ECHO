# MK1 Acoustic Taxonomy v1

**Status:** `FROZEN_V1`

## Principle

Labels describe observable acoustic phenomena. They do not assert incident cause, intent or human/legal interpretation.

## Target classes

### `GLASS_SHATTER`

Acoustic signature consistent with brittle glass breaking/shattering. Exclude generic impact without glass evidence. Confusers: ceramic, metal impacts, dishes, construction transients.

### `SIREN`

Sustained/modulated siren-like warning sound. Distinguish from generic periodic beeps/fire alarm where possible. Confusers: music/synth sweeps, vehicle electronics and other alarms.

### `FIRE_ALARM`

Acoustic signature specifically consistent with fire-alarm style patterns when mapping evidence supports that semantics. Do not map all `Alarm` clips here.

### `VEHICLE_HORN`

Vehicle horn/honking acoustic event. Confusers: whistles, alarms and tonal machinery.

### `TIRE_SQUEAL`

High-friction tire squeal/skid acoustic event. Confusers: brakes, metal squeal, machinery friction.

## Non-target states

`BACKGROUND_NO_TARGET` represents examples/windows containing none of the target classes and includes structured hard-negative families. `UNKNOWN` is a decision-layer abstention state when no target evidence is sufficient; it need not be a training neuron.

## Multi-label semantics

A window/event may contain multiple target classes. Training/evaluation therefore uses independent labels/scores and multilabel metrics rather than forcing one softmax class.

## Mapping governance

Source labels are categorized EXACT/NARROWER/BROADER/AMBIGUOUS/NEGATIVE/UNUSABLE. Human review is required for ambiguous mappings.

## Deferred classes

Vehicle collision, generic impact, yell/scream, reversing beeper and other candidates remain future/deferred; adding them is a versioned taxonomy change.

## Versioning

Published event payloads include taxonomy/schema version. A v2 change triggers review of dataset manifests, model heads, thresholds and downstream consumers.

## Validation

Per-class support/diversity, error analysis and confusion/hard-negative behavior determine whether each v1 target remains viable after MK1 evidence.