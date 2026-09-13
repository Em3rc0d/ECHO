# MK1 Data Foundry — Label Mapping v1

**Status:** `FROZEN_POLICY / CLIP_REVIEW_PENDING_WHERE_MARKED`

## 1. Principle

ECHO labels describe audible phenomena. Mapping is semantic and evidence-based, never a substring match. Source labels can be exact, narrower, broader, ambiguous, negative, or unusable relative to ECHO.

## 2. Relation types

| Relation | Meaning | Automatic positive admission? |
|---|---|---|
| `EXACT` | source concept matches the ECHO acoustic concept closely enough for dataset-level mapping | yes, subject to asset quality/license gates |
| `NARROWER` | source concept is a strict subtype of an ECHO target | normally yes; subtype identity retained |
| `BROADER` | source concept includes target and non-target phenomena | **no**; requires clip-level evidence/review |
| `AMBIGUOUS` | overlap cannot be established from source label alone | no |
| `NEGATIVE` | useful confuser/background for a target | negative only |
| `UNUSABLE` | semantics or annotation quality do not support intended use | no |

## 3. Frozen target definitions

### `GLASS_SHATTER`
Audible brittle glass break/shatter. Generic brittle-material shatter, dishes, ceramics or metal impact do not qualify without glass evidence.

### `SIREN`
Sustained/modulated warning siren. Distinct from short generic alarm beeps, reverse beepers, car alarms and music/synth sweeps.

### `FIRE_ALARM`
A fire/smoke/emergency alarm sound with source semantics specifically supporting that class. Generic `Alarm` is not sufficient.

### `VEHICLE_HORN`
Road-vehicle horn/honking event. Train horns, whistles and tonal machinery are not automatically mapped.

### `TIRE_SQUEAL`
High-frequency tire/road friction squeal or skid sound. Generic brake, metal squeal, machine friction or screech is not sufficient.

## 4. Mapping matrix

### FSD50K 1.0

| Upstream label | ECHO relation | ECHO target/use | Decision |
|---|---|---|---|
| `Shatter` | `BROADER` | candidate `GLASS_SHATTER` | clip-level glass confirmation required |
| `Glass` | `BROADER` | context/negative/candidate | glass object presence does not imply shattering |
| `Siren` | `EXACT` | `SIREN` | positive candidate |
| `Vehicle horn, car horn, honking` | `EXACT` | `VEHICLE_HORN` | positive candidate |
| `Alarm` | `BROADER` | alarm-family confuser | never auto-map to `FIRE_ALARM` |
| `Doorbell`, `Ringtone`, `Bell`, `Chime` | `NEGATIVE` | hard negatives for alarm/siren | negative/context |
| `Screech`, `Squeak` | `AMBIGUOUS/NEGATIVE` | tire-squeal confusers | not `TIRE_SQUEAL` |
| `Dishes, pots, and pans`, `Chink, clink`, `Crack`, `Slam` | `NEGATIVE` | glass-shatter confusers | negative/context |

`FIRE_ALARM` and `TIRE_SQUEAL` are not assumed present as released FSD50K target classes.

### SONYC-UST v2

| Upstream label | Relation | ECHO use |
|---|---|---|
| `car-horn` | `EXACT` | `VEHICLE_HORN` |
| `siren` | `EXACT` | `SIREN` |
| `car-alarm` | `NEGATIVE` | confuser for `SIREN` / `FIRE_ALARM` |
| `reverse-beeper` | `NEGATIVE` | confuser for `SIREN` / `FIRE_ALARM` |
| `other-unknown-alert-signal` | `AMBIGUOUS` | quarantine for positive mapping; usable as broad alert context only |
| machinery/non-machinery impacts | `NEGATIVE` | glass-shatter confusers unless another exact label is present |
| music / voice / dog / engines | `NEGATIVE` | background/context depending on clip polyphony |

Because SONYC is multilabel, a clip can simultaneously contain a valid target and other background classes. Negative context never deletes an independently positive target label.

### SINGA:PURA v1.0a

| Event code / label | Relation | ECHO use |
|---|---|---|
| `3-1 Glass breaking` | `EXACT` | `GLASS_SHATTER` |
| `5-1 Car horn` | `EXACT` | `VEHICLE_HORN` |
| `5-3 Siren` | `EXACT` | `SIREN` |
| `5-2 Car alarm` | `NEGATIVE` | alert confuser |
| `5-4 Reverse beeper` | `NEGATIVE` | alert confuser |
| `12-1 Friction brake` | `AMBIGUOUS/NEGATIVE` | useful tire-squeal confuser, not positive |
| `0-1 Screeching` | `AMBIGUOUS/NEGATIVE` | useful tire-squeal confuser, not positive |
| `3-0 Other non-machinery impact` | `NEGATIVE` | glass-shatter confuser |

Strong onset/offset annotations are retained as temporal evidence and may be converted to ECHO windows without discarding the original event interval.

### ESC-50

| Upstream label | Relation | ECHO use |
|---|---|---|
| `siren` | `EXACT` | `SIREN`, research-only profile |
| `car_horn` | `EXACT` | `VEHICLE_HORN`, research-only profile |
| other classes | `NEGATIVE` or `UNUSABLE` per confuser plan | research-only background/sanity |

### UrbanSound8K

| Upstream label | Relation | ECHO use |
|---|---|---|
| `siren` | `EXACT` | `SIREN`, research-only profile |
| `car_horn` | `EXACT` | `VEHICLE_HORN`, research-only profile |
| engine/traffic-like classes | `NEGATIVE` | urban hard negatives/context |
| unrelated urban classes | `NEGATIVE/UNUSABLE` | background/sanity |

### AudioSet

Ontology concepts `Shatter`, `Siren`, `Fire alarm`, `Vehicle horn, car horn, honking`, and `Tire squeal` are semantically useful references. The Foundry registry classifies AudioSet as `REFERENCE_ONLY` for raw media by default; a semantic mapping does not override source acquisition/rights policy.

## 5. Multi-label handling

Mapping produces a set of ECHO labels. It never forces mutually exclusive class selection. If one source interval contains both siren and vehicle horn evidence, both labels remain present.

For clip-level weak labels, the label applies to the clip/window only under the source annotation semantics. For strong labels, onset/offset are preserved and window labels are derived using a documented overlap rule in the later audio/window stage.

## 6. Manual review queue

Manual review is mandatory when:

- a positive mapping is `BROADER` or `AMBIGUOUS`;
- source metadata conflicts with the annotation;
- a clip contains a suspected target not represented in its source label;
- label quality flags are low/uncertain;
- a high-confidence model error suggests source-label contamination.

Review record:

```text
asset_id
source_label
echo_candidate
reviewer/review_version
decision
reason/evidence
reviewed_at
```

## 7. Mapping versioning

`configs/data_foundry/label_mapping.v1.json` is the machine-readable source of truth. Any mapping change creates a new mapping version/hash and invalidates downstream manifests/benchmarks that depended on the old mapping.

## 8. Stop-the-line examples

- `Alarm` -> `FIRE_ALARM` automatically: **forbidden**.
- `Screech` -> `TIRE_SQUEAL` automatically: **forbidden**.
- `Shatter` -> `GLASS_SHATTER` without glass evidence: **forbidden**.
- `car-alarm` -> `SIREN`: **forbidden**.

The Foundry prefers fewer high-integrity positives over larger semantically contaminated training data.