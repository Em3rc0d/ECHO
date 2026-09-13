# MK1 Rollback Plan

**Status:** `DESIGN_READY`

## Purpose

Even in a PoC, model/config/schema changes must be reversible enough to compare evidence and recover a known-good vertical.

## Versioned units

Code commit, dependency lock, dataset manifest, model/checkpoint, preprocessing config, taxonomy, thresholds/EventEngine config, schema version and broker config.

## Rollback triggers

Regression in frozen test/streaming replay, new false-alarm burst, runtime/capacity failure, incompatible schema consumer, invalid license/provenance or field-device breakage.

## Procedure

Identify last certified result bundle -> restore exact model/config/schema/runtime -> rerun smoke + relevant regression subset -> repoint active config/artifact -> preserve failed version/evidence for analysis.

## Data compatibility

Avoid destructive event-store migrations in MK1. New schema versions should preserve old evidence or provide an explicit transform.

## Model rollback

Model and calibration/EventEngine config are promoted together when their thresholds depend on score distribution. Do not roll back one without checking compatibility.

## MK2 evolution

Production blue/green/canary, signed artifacts and automatic rollback belong to MK2 after release topology is defined.

## Invalidation

Update when deployment/persistence model becomes more complex.