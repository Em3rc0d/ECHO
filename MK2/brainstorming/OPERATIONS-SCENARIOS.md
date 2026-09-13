# MK2 Operations Scenarios

**Status:** `SCENARIO_SET`

## Normal operation

N configured sources online, stable queues, model/event latency within SLO, broker/store healthy, no privacy/media-retention anomalies.

## Camera/network outage

One or many sources disconnect. Supervisors back off/reconnect; other sources continue; operator sees source-specific degradation; stale generation work is rejected.

## Inference overload

Queue lag rises. Scheduler enforces per-source fairness and bounded policy, records drops/staleness and triggers capacity health alert before memory exhaustion.

## Broker/store outage

Detection remains observable. Delivery durability/outbox behavior follows frozen MK2 policy. Recovery does not duplicate logical actions beyond idempotent semantics.

## Bad model release

Regression/field monitoring detects deterioration. Rollback restores compatible model+calibration/EventEngine config and records release lineage.

## Drift/new confuser

False alerts increase for a site/device. Evidence is captured through event/error metadata and approved samples; new data version enters offline retraining/regression, not automatic online learning.

## Security incident

Credential exposure or unauthorized publish triggers rotation/revocation, audit review and incident procedure without requiring model retraining.

## Upgrade/migration

Schema/config/model changes roll out with compatibility checks and rollback path; mixed-version behavior is explicitly supported or forbidden.

## Disaster/restart

Document which state is reconstructible from config/event store and what in-memory candidate events are lost; health reflects recovery.