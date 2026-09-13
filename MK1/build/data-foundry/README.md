# MK1 Data Foundry

**Status:** `TOOLCHAIN_IMPLEMENTED / REAL_CORPUS_INSTANCE_NOT_YET_CERTIFIED`

## Purpose

The MK1 Data Foundry converts heterogeneous public, sensor-network and future ECHO field audio into a traceable, versioned, license-aware and leakage-resistant corpus. It is part of `MK1/build` and implements the data path required before model A/B/C benchmarking.

## End-to-end contract

```text
publisher/source release
  -> acquisition registry + checksum verification
  -> source-specific metadata intake
  -> RawAssetCandidate manifest
  -> local asset SHA-256
  -> rights policy
  -> semantic mapping + manual review where required
  -> technical quality
  -> group identity + duplicate screening
  -> protected split / field holdout
  -> frozen asset/split/report bundle
  -> dataset manifest hashes
  -> benchmark handoff
```

No mandatory link may be skipped. Missing rights, provenance, local file, group identity or required review produces quarantine/rejection rather than silent admission.

## Implemented code surface

```text
src/echo/data_foundry/
  acquisition.py     publisher bundle verification
  adapters.py        FSD50K/SONYC/SINGA:PURA/ESC-50/UrbanSound8K metadata adapters
  admission.py       per-asset rights + mapping + quality decision
  contracts.py       dataset-neutral typed contracts
  dedup.py           group/exact/registered-near-duplicate leakage audits
  fingerprints.py    PCM-WAV normalized-envelope screening fingerprint
  hashing.py         canonical JSON + SHA-256 helpers
  intake.py          config-driven candidate-manifest production
  manifest.py        canonical asset/dataset manifests
  mapping.py         versioned semantic label mapping
  pipeline.py        admission, split and freeze orchestration
  policies.py        rights/use decisions
  quality.py         candidate quality checks
  registry.py        source registry validation
  reports.py         coverage/quarantine reports
  reviews.py         manual review evidence
  splits.py          deterministic group-aware splitting
  cli.py             executable Foundry commands
```

Machine-readable policies live in `configs/data_foundry/`; JSON contracts live in `schemas/data_foundry/`; tests live in `tests/data_foundry/`.

## Data zones

```text
EXTERNAL / LANDING
  immutable publisher bundle or authorized field capture
        ↓
STAGING
  parsed source metadata / candidates
        ↓
QUARANTINE  ← rights / semantic / technical uncertainty
        ↓
CURATED
  hashed + mapped + reviewed + grouped assets
        ↓
FROZEN
  train | validation | test | field_holdout
```

Large audio is not committed to Git. Git stores source/policy registries, schemas, code, manifests, hashes, reports and certification evidence.

## Frozen MK1 taxonomy

`GLASS_SHATTER`, `SIREN`, `FIRE_ALARM`, `VEHICLE_HORN`, `TIRE_SQUEAL`.

`BACKGROUND_NO_TARGET` is a data state and hard-negative role. `UNKNOWN` is a decision-layer abstention state, not an automatically trained sixth class.

## Source roles

FSD50K supplies broad/mixed-license environmental candidates and requires asset-level rights filtering. SONYC-UST supplies urban sensor-domain multilabel data. SINGA:PURA supplies strongly labelled urban sensor examples but ShareAlike use requires the chosen profile to respect policy. ESC-50 and UrbanSound8K are research-only in the default policy. AudioSet is ontology/pretraining/reference evidence rather than a default raw-media source. ECHO Field Dataset remains gated by authorized device/site collection.

## Known sourcing gaps

The Foundry never fabricates `FIRE_ALARM` or `TIRE_SQUEAL` from generic alarm/screech/friction labels. If a frozen real manifest lacks direct valid evidence, the generated coverage report keeps the gap visible and the model benchmark cannot pretend the class is certified.

## CLI execution

```bash
# 1. verify publisher release files
echo-data-foundry acquisition-plan fsd50k-1.0 --stage metadata
echo-data-foundry verify-acquisition fsd50k-1.0 /data/landing/fsd50k --stage metadata

# 2. parse source metadata to deterministic candidate JSONL
echo-data-foundry intake work/intake-sonyc.json work/sonyc-candidates.jsonl

# 3. hash / rights / mapping / review admission
echo-data-foundry admit work/candidates.jsonl work/records.jsonl \
  --profile release_safe --audio-root /data/curated --reviews work/reviews.json

# 4. assign splits, audit leakage and freeze evidence
echo-data-foundry freeze work/records.jsonl work/frozen/echo-mk1-data-001 \
  --manifest-id echo-mk1-data-001 --profile release_safe
```

## Freeze outputs

`asset-manifest.jsonl`, `split-manifest.json`, `dataset-manifest.json`, `coverage-report.json`, `dedup-report.json`, `quarantine-report.json`.

A benchmark without the exact frozen component hashes is non-certifiable.

## Stop-the-line rules

Stop downstream execution on unknown/incompatible rights, release checksum mismatch, missing file/hash, broad positive mapping without review, group or duplicate leakage across protected splits, field-holdout contamination, mutable manual file selection, or a report that cannot reconstruct its asset population.

## Certification boundary

The complete Foundry software/toolchain can be tested and certified without downloading tens of gigabytes into CI. **A real corpus certificate cannot be fabricated**: `EMP-DATASET-001`, `EMP-DATA-QUALITY-001` and `CERT-MK1-DF-CORPUS-001` require the declared external source media to be acquired and the implemented pipeline to run against it.

See `ACQUISITION.md`, `METADATA-INTAKE.md`, `SEMANTIC-REVIEW.md`, `CORPUS-FREEZE.md` and `FOUNDRY-GATES.md` for gate-level details.
