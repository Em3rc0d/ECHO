# MK2 Resilience Architecture

**Status:** `DESIGN_SPECIFIED`

## Objectives

Recover predictably from source, process, model, broker, storage and network failures while keeping unaffected sources operating and avoiding duplicate/stale events.

## Source resilience

Supervised adapters, exponential backoff+jitter, generation IDs, stall detection and explicit offline/degraded state. Permanent auth/config errors avoid retry storms.

## Worker resilience

Worker crash isolates in-flight work; scheduler expires stale generation/deadline items. Restart does not silently reuse incompatible model/config state.

## Broker/storage resilience

Health/circuit behavior prevents indefinite blocking. Durability/outbox policy depends on production SLO. Recovery preserves event IDs and avoids duplicate logical events.

## Process/host resilience

Service supervision restarts crashed components. HA/multi-host redundancy is only added if availability targets justify it; otherwise document recovery time and single-host limitation.

## Configuration/model resilience

Validated immutable release bundles, health checks after activation and rollback to previous certified bundle.

## Chaos/fault testing

Kill decoder/worker/broker, network partition, packet loss/stall, disk/full/read-only store, bad config/model checksum and load saturation.

## Metrics

MTTR/recovery time, event loss/duplicates, source downtime, queue behavior, stale work rejection and SLO impact.

## Invalidation

Final redundancy/retry parameters depend on frozen MK2 SLO/profile.