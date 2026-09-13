# Quarry — FIRE_ALARM and TIRE_SQUEAL data gaps

**Status:** `CANDIDATE_SOURCE_PATH / NOT_ADMITTED`  
**Purpose:** close exact-class coverage gaps without broad-label coercion.

## 1. Problem

The current selected released corpora provide strong evidence for `SIREN`, `VEHICLE_HORN` and `GLASS_SHATTER`, but the default release-safe path still lacks a clean exact-class pool for:

```text
FIRE_ALARM
TIRE_SQUEAL
```

Generic `Alarm`, `Screech`, `Screeching`, `Friction brake` or similar labels are not accepted as substitutes.

## 2. Evidence found

The original FreesoundDataset annotation explorer exposes exact AudioSet-category candidate/ground-truth pools that were not included in FSD50K's released 200-class vocabulary:

```text
Fire alarm  -> 87 candidate samples, 24 ground-truth examples
Tire squeal -> 23 candidate samples, 10 ground-truth examples
```

Evidence pages:

- `https://fsannotator.upf.edu/fsd/explore/%252Fm%252F0c3f7m/` — Fire alarm.
- `https://fsannotator.upf.edu/fsd/explore/%252Fm%252F0h9mv/` — Tire squeal.

These counts describe the historical annotation explorer, **not an admitted ECHO corpus**.

## 3. Correct acquisition path

The safe/defensible path is an ECHO-curated extension, not pretending these assets belong to FSD50K v1.0:

```text
FreesoundDataset exact-category evidence
        ↓
source clip IDs
        ↓
individual upstream asset provenance + license
        ↓
allow only policy-compatible assets
        ↓
manual semantic confirmation
        ↓
local media SHA-256 + technical probe
        ↓
group/dedup/split gates
        ↓
ECHO curated source manifest
```

Proposed future source ID after first real acquisition:

```text
echo-freesound-exact-gap-v1
```

It must not be added to the certified source registry before real asset identities/licenses are resolved.

## 4. Admission requirements

Each candidate must have:

- immutable upstream/source ID;
- origin URL/provenance;
- exact source-category evidence;
- current per-asset license and attribution metadata;
- ECHO use decision;
- manual review record confirming the target event is actually present;
- SHA-256 of acquired bytes;
- duration/sample-rate/channel probe;
- defensible recording/uploader grouping;
- duplicate and near-duplicate screening.

Unknown or incompatible rights fail closed into quarantine.

## 5. Semantic stop-lines

`FIRE_ALARM` requires evidence of the acoustic alarm event itself. Smoke-alarm-like, generic bell, buzzer, siren or arbitrary alert audio is not auto-promoted.

`TIRE_SQUEAL` requires the specific tire/road friction event. Generic squeak, metal screech, brake sound, or unrelated friction noise is not auto-promoted.

## 6. Sufficiency

The historical exact-category counts are small enough that they should be treated as a bootstrap pool, not proof of sufficient diversity. ECHO still needs diversity across devices, environments, recording chains and background conditions, plus field/replay evaluation.

If the curated exact pool remains too small, the correct outcome is:

```text
COVERAGE_GAP_REMAINS_OPEN
```

not synthetic inflation of empirical claims.

## 7. Certification path

```text
Q-GAP-FIRE-TIRE
   -> curated candidate manifest
   -> rights + semantic review
   -> EMP-DATASET-001 counts
   -> EMP-DATA-QUALITY-001 diversity/duplicate evidence
   -> source/corpus certificate only if gates pass
```

This quarry closes the research question of *where defensible exact-label candidates exist*, but intentionally does not close the empirical corpus node before the bytes are acquired and reviewed.
