# MK1 Dataset Selection Evidence

**Status:** `PENDING_MANIFEST_EXECUTION`

## Purpose

Record what assets/classes actually survived MK0's semantic, license and duplicate filters. This is the empirical companion to `Q-DATASETS.md`.

## Required per-source report

Dataset release/version, candidate assets, admitted/quarantined/rejected counts, rejection reason distribution, license distribution, source/uploader groups, duplicate/near-duplicate findings and ECHO label mapping categories.

## Per-class report

For each target: unique groups, events/clips, duration, source diversity, train/validation/test distribution and priority hard negatives. Do not report only total clips.

## Split audit

Zero forbidden source/recording group overlap between train and test; field holdout separate; list any compromises explicitly.

## Manifest identity

Record manifest/taxonomy/mapping/split hashes. Benchmark result bundle references these hashes.

## Status discipline

No numeric counts are inserted before running the admission process. Placeholder fields remain clearly `PENDING`.

## Invalidation

New asset, corrected label/license, deduplication finding or taxonomy change creates a new manifest version.