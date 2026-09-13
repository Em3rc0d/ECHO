# MK1 Dataset Selection Evidence

**Status:** `FOUNDRY_FOUNDATION_READY / CORPUS_EXECUTION_PENDING`

## Purpose

Record what assets/classes actually survive MK0/MK1 semantic, license, provenance, duplicate and split gates. This is the empirical companion to `MK0/quarries/Q-DATASETS.md` and the build-time Data Foundry.

## Foundation now available

The repository now contains:

- `configs/data_foundry/source_registry.v1.json` — seven source families with declared role/license/coverage;
- `configs/data_foundry/label_mapping.v1.json` — explicit semantic mapping and hard-negative relations;
- `configs/data_foundry/license_policy.v1.json` — release-safe vs research-only/review/quarantine decisions;
- JSON schemas for source registry, asset records and dataset manifests;
- metadata adapters for FSD50K, SONYC-UST, SINGA:PURA, ESC-50 and UrbanSound8K;
- SHA-256/canonical-manifest logic;
- deterministic group-aware split primitives;
- exact-duplicate and metadata-quality checks;
- admission orchestration that fails closed on rights/mapping uncertainty;
- CI evidence across Python 3.10–3.12.

## Source-level coverage known before corpus execution

`SIREN` and `VEHICLE_HORN` have multiple direct source families. `GLASS_SHATTER` has direct strong-label evidence from SINGA:PURA plus broader FSD50K `Shatter` candidates requiring glass-specific review. `FIRE_ALARM` and `TIRE_SQUEAL` remain explicit acquisition gaps for the default release-safe profile; they are not manufactured from generic alarm/screech/brake labels.

This is a source-level statement only. It is **not** a final count or data-sufficiency claim.

## Required per-source execution report

For every acquired source release record:

```text
source release/version + canonical provenance
candidate assets
locally present/hashable assets
admitted/quarantined/rejected counts
rejection/quarantine reason distribution
license distribution
source/uploader/sensor/recording groups
exact duplicate clusters / label conflicts
near-duplicate findings when that stage is implemented
mapping categories and manual-review outcomes
```

## Per-class report

For each target report unique independent groups, events/clips, duration, source diversity, profile/license distribution, train/validation/test distribution and priority hard-negative coverage. Never report only raw clip count.

## Split audit

Required protected-boundary invariants:

- zero recording/source group overlap across prohibited splits;
- zero exact-content hash overlap across prohibited splits;
- field holdout separated from all training/calibration;
- augmented/derived samples inherit parent split;
- source-provided folds/sensor/time relationships retained as evidence.

## Manifest identity

The benchmark consumes only frozen Foundry outputs and records at least:

```text
source_registry_sha256
license_policy_sha256
label_mapping_sha256
split_policy_sha256
asset_manifest_sha256
split_manifest_sha256
profile
```

Any asset or policy change creates a new data identity.

## Current empirical nodes

`EMP-DATASET-001 = OPEN` — exact admitted corpus/assets/counts/durations.  
`EMP-DATA-QUALITY-001 = OPEN` — duplicate/quality/group-diversity findings.  
`CERT-MK1-DF-CORPUS-001 = OPEN` — requires DF-G0..DF-G8 to pass for one named profile/manifest.

## No fabricated metrics

Numeric corpus results remain absent until source releases and audio are actually acquired and passed through the Foundry. Source headline counts in the catalog are evidence about upstream releases, not admitted ECHO counts.

## Invalidation

New asset, corrected label/license, deduplication finding, source release change, taxonomy change or split-policy change creates a new manifest lineage and may invalidate dependent benchmark results.