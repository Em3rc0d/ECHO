# MK1 Data Foundry — Split, Grouping and Deduplication Policy

**Status:** `FROZEN_METHOD / EMPIRICAL_DUPLICATE_RESULTS_PENDING`

## 1. Goal

Prevent optimistic evaluation caused by related recordings, slices, sensors, sessions or near-duplicate audio appearing on both sides of a protected evaluation boundary.

## 2. Core rule

**Split groups, not clips.** The clip is often not the independent experimental unit.

Preferred group hierarchy:

```text
physical event/session
  > original recording
  > source/uploader + occurrence
  > sensor/site/time block
  > clip only when no stronger relation exists
```

When multiple candidate group IDs exist, use the most conservative relation that prevents leakage and preserve the underlying IDs as metadata.

## 3. Source-specific grouping

### FSD50K

Use Freesound clip/uploader/source metadata as available. Exact duplicates share a hash. When multiple clips are known to derive from the same recording/uploader event family, keep them in one protected group. If group metadata is insufficient for a test candidate, flag rather than invent independence.

### ESC-50

Preserve `src_file` as source identity; the `take` field represents fragments from the same original source. Do not treat takes as independent across protected splits. Retain original fold.

### UrbanSound8K

Use `fsID` and `occurrenceID`; multiple slices from the same occurrence remain grouped. Preserve official fold metadata; do not randomize slices independently.

### SONYC-UST

Preserve sensor identity and upstream split/time metadata. For ECHO-specific derived sets, sensor/time relationships are part of group design; do not allow a split method that makes the same short recording or derived segment cross boundaries.

### SINGA:PURA

Preserve `sensor_id` plus recording identity. Strong events from the same 10-second recording stay together. If repeated/adjacent recordings are later shown to form a session, session grouping supersedes individual-file grouping.

### ECHO Field

Group by controlled recording session, source/device/site and event instance. Multiple windows from one event never span train/test. Repeated playback/augmentation derivatives stay with their parent source asset.

## 4. Split profiles

The code contains **no hidden default train/validation/test ratio**. A split profile must declare explicit ratios or source-locked assignments, seed and grouping rules.

The benchmark can freeze one profile after corpus counts/diversity are known. Changing ratios/seed/grouping creates a new split-manifest identity.

## 5. Field holdout

Field holdout is not a fourth random bucket. It is an independently governed evaluation population. It is excluded from:

- model fitting;
- architecture selection;
- augmentation design driven by its errors;
- early stopping;
- threshold/calibration tuning;
- Event Engine parameter tuning.

If any field clip is promoted into development/training, a new untouched field holdout must remain and the data version changes.

## 6. Exact duplicate detection

SHA-256 equality means the bytes are exact duplicates. Duplicate assets may be retained only when provenance requires recording both references, but one canonical content identity controls split placement. Conflicting labels on identical bytes enter review.

## 7. Near-duplicate roadmap

MK1 Foundry v1 records the interface for near-duplicate evidence but does not invent fingerprint confidence before implementation. Planned checks include robust audio fingerprints/embeddings for:

- transcoded copies;
- cropped/shifted versions;
- normalized/gain-changed copies;
- dataset overlap through common Freesound originals;
- augmented derivatives accidentally entering evaluation.

Any discovered cross-test near duplicate is a stop-the-line issue until resolved.

## 8. Augmentation lineage

Synthetic/augmented samples receive `parent_asset_ids`/generation lineage in derived manifests. Parent and all derivatives inherit the parent's split. Augmentation is applied after split assignment, never before grouping.

## 9. Deterministic assignment

For groups without locked upstream assignments, `src/echo/data_foundry/splits.py` hashes `seed + group_id` into an explicit ratio profile. Determinism allows independent reproduction. Changing the seed is a new split version, not an innocuous rerun.

## 10. Audit outputs

Required:

```text
group_count by source/class/split
assets per group distribution
exact duplicate clusters
label conflicts among identical hashes
cross-split group overlap = 0
cross-split exact-hash overlap = 0
field-holdout overlap = 0
near-duplicate findings when implemented
```

## 11. Invalidation

New provenance revealing hidden relationships, duplicate discoveries, source-release changes or a split policy change invalidates affected data/benchmark certificates and requires fresh manifests.