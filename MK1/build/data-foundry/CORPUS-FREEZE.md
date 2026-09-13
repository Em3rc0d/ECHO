# Data Foundry — Corpus Freeze and Handoff

**Status:** `IMPLEMENTED / CORPUS INSTANCE REQUIRES REAL SOURCE EXECUTION`

## Purpose

The freeze stage turns reviewed `AssetRecord` rows into the only data bundle that the MK1 benchmark may consume. It assigns protected splits, audits duplicate leakage, emits coverage/quarantine evidence and binds every output to policy/config hashes.

## Freeze flow

```text
AssetRecord JSONL
   ↓ split policy
split assignment
   ↓ group + duplicate audit
admitted asset manifest
   + split manifest
   + coverage report
   + duplicate report
   + quarantine/rejection report
   ↓
dataset-manifest.json
```

## Split policy

`configs/data_foundry/split_policy.v1.json` preserves recognized upstream train/validation/test semantics when present. Unpartitioned groups use deterministic SHA-256 group hashing with the frozen seed and fallback 70/15/15 allocation. The percentage is a deterministic fallback, not a claim that every upstream dataset must be re-split. Field holdout is always isolated.

## Duplicate controls

The freeze gate checks:

- one `recording_group_id` cannot cross splits;
- identical SHA-256 content cannot cross splits;
- assets carrying the same registered `near_duplicate_fingerprint` cannot cross splits.

`near_duplicate_fingerprint` is a screening signal, never a replacement for SHA-256. The Foundry includes a lightweight PCM-WAV envelope fingerprint helper; unsupported codecs can supply a decoder-derived fingerprint through the same record field.

## Generated outputs

A freeze produces:

```text
asset-manifest.jsonl
split-manifest.json
dataset-manifest.json
coverage-report.json
dedup-report.json
quarantine-report.json
```

The dataset manifest binds source registry, license policy, label mapping, split policy, asset manifest and split manifest identities by SHA-256.

## Coverage semantics

A freeze may technically complete while reporting target coverage gaps. The status becomes `PASS_WITH_COVERAGE_GAPS`; this does not authorize model-selection claims for missing classes. `CERT-MK1-DF-CORPUS-001` requires the named benchmark profile to satisfy its declared data sufficiency criteria, not merely produce files.

## CLI

```bash
echo-data-foundry admit work/candidates.jsonl work/records.jsonl \
  --profile release_safe --audio-root /data/curated

echo-data-foundry freeze work/records.jsonl work/frozen/mk1-release-safe \
  --manifest-id echo-mk1-data-001 --profile release_safe
```

## Reproducibility gate

Running freeze again over byte-identical records and unchanged policy inputs must reproduce asset/split/policy hashes. `dataset-manifest.json` includes a creation timestamp, so its whole-file digest may differ if regenerated with a different timestamp; benchmark identity is anchored to the component hashes inside it.

## Benchmark handoff

Training code is forbidden from enumerating arbitrary directories. It must consume the frozen manifest and explicit split assignment. Manual addition/removal of files after freeze creates a different corpus and invalidates the benchmark run.

## Stop-the-line

Cross-split group/duplicate leakage, missing policy identity, mutable manual selection, or a field-holdout asset in development splits is a FAIL. Fix upstream data lineage and regenerate rather than patching the frozen bundle in place.
