# MK2 SLO Framework

**Status:** `FRAMEWORK_FROZEN / NUMBERS_PENDING MK1`

## Why SLOs are multidimensional

ECHO can have high classifier F1 but still fail operationally through false alarms, stale processing or unavailable sources. Production SLOs therefore cover ML quality, event quality, latency, availability, capacity and delivery.

## Quality dimensions

Per-class event recall/miss rate, false alarms/source-hour, precision/F1/PR-AUC as diagnostics, calibration and field-holdout performance by relevant condition.

## Timing

Source freshness, inference latency, confirmation latency, end-to-end event latency and queue lag p95/p99. Separate camera/network from core runtime where possible.

## Availability

Source ingest availability (when source itself is healthy), inference service availability, broker/publisher health and event-delivery success. Do not blame ECHO for an externally powered-off camera without separate attribution.

## Capacity

Maximum supported N under declared hardware/model/source window rate while meeting lag/drop/latency/quality constraints over soak duration.

## Error budget

For production profiles, define acceptable periods of degraded availability/latency and how releases are halted when error budget is exhausted. Exact policy follows deployment criticality.

## Freeze procedure

Use MK1 baseline evidence -> choose achievable but meaningful TARGETs -> freeze before MK2 final tests -> evaluate holdout/load/soak. Never move SLO after seeing failure without a new decision/version.

## Invalidation

Major model/hardware/topology/site class can require a new SLO profile.