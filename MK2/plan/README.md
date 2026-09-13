# MK2 / Plan

**Status:** `SPECIFIED / VALUES DEPEND ON MK1`

## Purpose

Translate measured MK1 behavior into an ordered hardening/release program. The plan covers capacity, scale topology, CI/CD, model release, migrations, incidents and final certification.

## Planning rule

First freeze a deployment profile and SLOs from evidence; then harden. Do not build distributed complexity before a bottleneck/availability requirement justifies it.

## Sequence

Capacity baseline -> scale/backpressure -> resilience/delivery durability -> observability/security -> model/release pipeline -> migration/incident drills -> load/soak/chaos/regression -> release certification.

## Artifacts

`CAPACITY-PLAN.md`, `SCALE-PLAN.md`, `CI-CD-PLAN.md`, `MODEL-RELEASE-PLAN.md`, `MIGRATION-PLAN.md`, `INCIDENT-PLAN.md`, `RELEASE-PLAN.md`.

## Evidence

Every plan step names expected metrics/result artifacts and rollback criteria. Release does not proceed on undocumented manual confidence.

## Invalidation

Major deployment profile, model or SLO change requires re-planning affected workstreams.