# MK2 Product Contracts

**Status:** `DESIGNED / VERSION VALUES PENDING MK1`

## Compatibility surface

Source, raw-inference, event, state/telemetry and config schemas become explicit public/internal compatibility boundaries. Production consumers should not depend on Python classes or model tensor layout.

## Version rules

Semantic-version-like policy: breaking schema/topic/meaning change increments major version; additive optional fields can be minor under consumer compatibility tests. Taxonomy version is independent but referenced by event payload.

## Model/config coupling

A production model release includes preprocessing, calibration and EventEngine config compatibility. Promotion/rollback treats them as a release bundle when score distribution affects thresholds.

## Source contract

Source IDs remain stable logical identities; hardware replacement can create a new device/session metadata version without changing consumers.

## Delivery contract

Confirmed event identity is stable across retries. Ordering is source-scoped unless a stronger global guarantee is explicitly introduced. Delivery semantics are documented independently from event truth.

## Health contract

Source health, system health and target events stay separate so a monitoring system does not interpret `OFFLINE` as an acoustic event.

## Deprecation

Production version removal requires telemetry/evidence that consumers migrated, a defined overlap window or explicit breaking release.

## Validation

Contract tests run across current + supported previous versions in CI/release certification.