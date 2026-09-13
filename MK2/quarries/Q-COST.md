# Quarry — Cost

**Status:** `FRAMEWORK_READY / REAL COSTS PENDING DEPLOYMENT`

## Purpose

Avoid treating open-source software as “free” when hardware, power, storage, network, operations and engineering time still exist.

## Cost dimensions

Compute hardware/accelerators; energy/thermal; storage for events/logs/models/optional clips; network/VPN/cloud egress if used; broker/database/observability services; device/microphone upgrades; maintenance/incident/operator time; model retraining/evaluation; compliance/security tooling.

## Profiles

Compare local CPU, local GPU/accelerator, centralized server and optional cloud. Use measured source capacity so cost can be normalized per supported source/site.

## Hidden trade-offs

A heavier model can increase hardware cost; cloud can reduce local maintenance while increasing recurring/network/privacy dependencies; media retention can dominate storage/compliance cost.

## Metric examples

Cost/source/month, watts/source, storage GB/source/day for metadata/log policy, engineering/operator effort per release and incremental cost for redundancy.

## Decision

PoC prioritizes free/open-source/local tools where practical. MK2 selects cost profile only after SLO/capacity evidence.

## Invalidation

Pricing/hardware/topology/retention changes require refreshed cost model.