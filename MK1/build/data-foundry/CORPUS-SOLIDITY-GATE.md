# MK1 Corpus Solidity Gate

**Status:** `ENFORCED_FOR_RELEASE_SAFE_FREEZE`  
**Policy:** `MK1-CORPUS-SOLIDITY-001`

The MK1 corpus is not considered certified merely because every target label appears once. A release-safe ECHO corpus must pass a versioned, fail-closed coverage and diversity gate before it can be handed to the benchmark.

## Certification floor

For every frozen target class:

- at least **50 admitted assets**;
- at least **25 independent recording groups**;
- at least **2 independent source datasets**;
- at least **180 s of positive clip exposure**;
- train: at least **20 assets / 10 groups**;
- validation: at least **5 assets / 3 groups**;
- test: at least **5 assets / 3 groups**;
- no source may contribute more than **80%** of one class.

The development corpus must also contain at least **200 background/hard-negative assets**, **50 independent negative groups**, and **3 negative sources**.

These values are a **minimum engineering certification floor**, not a claim that this amount of data guarantees a particular F1/recall result. Model sufficiency remains empirical and is decided by the benchmark.

## Hard rules

```text
field_holdout != development coverage
synthetic augmentation != independent source
broad/ambiguous label != exact target coverage
one duplicated recording != multiple independent groups
AudioSet annotation != redistribution right to underlying media
```

The field holdout is excluded from coverage calculations. It may validate domain behavior later but may never be used to hide a train/validation/test gap.

## FIRE_ALARM / TIRE_SQUEAL

These labels remain the highest-risk data nodes. The gap-closing plan is deliberately multi-source:

```text
FreesoundDataset exact-category candidates
        +
ECHO controlled-development recordings (authorized)
        +
other individually licensed exact public assets when provenance is defensible
        ↓
manual semantic review
        ↓
per-asset rights decision
        ↓
SHA-256 + audio probe
        ↓
group/dedup/split
        ↓
coverage policy
```

`AudioSet` remains useful as ontology/coverage evidence, but its annotation count does not automatically authorize acquisition or redistribution of the underlying media.

A separate `ECHO Field Dataset` stays untouched as holdout and does not count toward the 50/25/2 development floor.

## Stop line

A release-safe freeze with any unmet rule returns:

```text
FAIL_COVERAGE_GATE
```

and its frozen bundle is not eligible for benchmark handoff or `CERT-MK1-DF-CORPUS-001`.

The exact policy lives in:

`configs/data_foundry/coverage_policy.v1.json`
