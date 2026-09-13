# MK1 Dataset Selection Evidence

**Status:** `TOOLCHAIN_CERTIFIED / REAL_MANIFEST_EXECUTION_PENDING`

## Purpose

Record what assets/classes actually survive MK0/MK1 semantic, rights, technical-quality and duplicate/leakage filters. This is the empirical companion to `Q-DATASETS.md` and the executable Data Foundry.

## Current boundary

The Foundry specification and complete G0..G8 toolchain are certified. Exact source-media counts are **not** inserted before `EXEC-DATA-001` acquires and runs the declared real releases. This document therefore tracks the evidence contract without fabricating numbers.

## Required per-source report

For every executed source/release record:

```text
source_id + release
publisher acquisition verification
candidate assets
admitted / quarantined / rejected counts
rejection/quarantine reason distribution
license distribution
source/uploader/recording groups
technical-probe failures
exact/near duplicate findings
ECHO mapping categories
source split preservation/fallback behavior
```

## Required per-class report

For `GLASS_SHATTER`, `SIREN`, `FIRE_ALARM`, `VEHICLE_HORN`, `TIRE_SQUEAL` report:

- admitted positive assets;
- independent recording/source groups;
- duration and/or event count where meaningful;
- source diversity;
- train/validation/test distribution;
- hard-negative/confuser coverage;
- ambiguous/reviewed candidates;
- gaps that remain after admission.

Do not report only total clip count.

## Rights/profile split

At minimum distinguish:

- `release_safe`: assets compatible with the selected reusable/release-safe policy;
- `research_extended`: may include assets allowed only for academic/research evaluation under recorded terms;
- `field_holdout`: authorized deployment-domain evidence isolated from training unless a later policy explicitly changes that status.

A research-only result cannot silently populate a release-safe manifest.

## Technical-quality evidence

Real execution records local SHA-256, file size, technical audio probe, codec/sample rate/channels/duration when discoverable, and quarantine reasons for missing/corrupt/unprobeable media. Registered near-duplicate fingerprints and exact-byte label conflicts feed the dedup report.

## Split audit

Required result:

```text
group overlap across protected splits        = 0
exact SHA duplicate overlap across splits    = 0
registered near-duplicate overlap            = 0
field holdout contamination                  = 0
```

Any non-zero forbidden overlap is stop-the-line, not a caveat to hide in prose.

## Manifest identity

The executed evidence records hashes for source registry, license policy, label mapping, split policy, asset manifest and split manifest. Benchmark result bundles reference these identities through the validated frozen-bundle handoff.

## Known sourcing concerns before execution

Research currently predicts stronger multi-source support for `SIREN` and `VEHICLE_HORN`; `GLASS_SHATTER` has direct plus reviewable candidates; `FIRE_ALARM` and `TIRE_SQUEAL` require defensible direct assets if the real release-safe execution confirms the gap. Generic alarm/screech/friction labels are not coerced into narrower targets.

This is a sourcing hypothesis/landscape statement, not an achieved corpus result.

## Closure outputs

`EXEC-DATA-001` must generate:

```text
EMP-DATASET-001
EMP-DATA-QUALITY-001
asset-manifest.jsonl
split-manifest.json
dataset-manifest.json
coverage-report.json
dedup-report.json
quarantine-report.json
```

Only after DF-G0..DF-G8 pass against that named profile/manifest can `CERT-MK1-DF-CORPUS-001` become `CERTIFIED`.

## Invalidation

A source release change, corrected license/label, taxonomy/mapping change, probe/dedup finding or split-policy change creates a new corpus version rather than editing historical evidence in place.
