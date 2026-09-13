# MK1 Data Plan

**Status:** `READY_FOR_MANIFEST_BUILD`

## Objectives

Materialize the MK0 dataset policy into a versioned corpus for the five targets, explicit hard negatives/background and untouched field holdout when available.

## Steps

Ingest upstream metadata/assets -> verify license/provenance -> hash -> semantic mapping -> quality/dedup -> grouping -> split -> freeze manifest.

## Required reports

Per target: admitted assets, independent groups, total duration/event count, source/uploader diversity, license distribution, ambiguous exclusions and hard-negative coverage.

## Splits

Training/validation/test are group-aware. Field holdout is separate. Test data cannot guide augmentation, head capacity, thresholds or EventEngine parameters.

## Hard negatives

Seed confuser families from MK0, then after first model run mine high-confidence false positives from long negative audio. Add reviewed examples to future training version without changing frozen test.

## Versioning

Manifest/taxonomy/mapping/split hashes are benchmark inputs. Any admitted asset change creates a new data version.

## Field data

When authorized, device/site recordings preserve codec/device/distance/noise metadata and permitted use. Some field samples may be holdout-only and legally/ethically excluded from training.

## Completion

Data plan is complete when the benchmark can be reproduced from a manifest without manual file selection.