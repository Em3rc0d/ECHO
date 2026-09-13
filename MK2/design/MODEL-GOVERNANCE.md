# MK2 Model Governance

**Status:** `DESIGN_SPECIFIED`

## Model identity

Every production artifact has model ID/version, architecture code commit, checkpoint hash, preprocessing version, taxonomy version, training dataset manifest, training config/seed(s), calibration and compatible EventEngine config.

## Promotion stages

```text
EXPERIMENTAL -> CANDIDATE -> STAGING -> CERTIFIED -> ACTIVE -> DEPRECATED/ROLLED_BACK
```

Promotion requires reproducible benchmark, regression comparison and supply-chain/license checks.

## Registry metadata

Quality metrics per class/condition, streaming false alarms/misses, runtime profile, compatible schema/config range, known limitations, creator/build provenance and signed/hash identity where MK2 tooling supports it.

## Regression

A new model cannot silently trade a critical class for aggregate improvement. Compare same frozen regression/field suites and report statistically/operationally meaningful changes.

## Calibration coupling

Thresholds/calibrator/EventEngine config are versioned with model because score distributions change. A rollback restores a compatible bundle.

## Drift

Operational drift evidence triggers offline review/data collection and a new model version. No unsupervised online self-modification is required for MK2.

## Rollback

Keep at least one previous certified artifact/config deployable. Rollback test is part of release certification.

## Security/license

Checkpoint origin/hash/license and runtime dependencies are required before promotion.