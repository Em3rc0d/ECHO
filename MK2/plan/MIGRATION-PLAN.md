# MK2 Migration Plan

**Status:** `SPECIFIED`

## Migration domains

Event/schema versions, config format, model/preprocessing bundles, broker topics, persistence schema and deployment topology.

## Compatibility strategy

Prefer additive/backward-compatible changes. Breaking changes receive new major schema/topic/config version with explicit consumer migration and overlap period when feasible.

## Data migration

Structured event/history migrations are reversible or backed up. Raw continuous audio is not a migration dependency because it is not retained by default.

## Model migration

New model can require new thresholds/calibrator but should emit the same event contract unless taxonomy semantics change. A taxonomy change is a larger migration with consumer/data impacts.

## Source migration

Camera/device replacement updates source/device metadata while preserving stable logical `source_id` only when it represents the same intended monitoring point and audit semantics.

## Rollout

Dry-run in staging with production-like data/replay -> compatibility tests -> backup/snapshot -> controlled migration -> validation -> rollback window.

## Evidence

Migration runbook, before/after schema versions, data counts/checksums, consumer compatibility and rollback test.

## Invalidation

Update for any new persistent service or cross-site deployment.