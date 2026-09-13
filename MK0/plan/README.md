# MK0 / Plan

**Status:** `CERTIFIED_PLAN`

## Purpose

Plan converts research/design/architecture into executable experiments and closure criteria. It answers what must be measured before implementation, what evidence each experiment produces, how results remain comparable and what is allowed to remain external.

## Inputs

Frozen problem boundary, candidate/final taxonomy, model/data/source research, architecture boundaries, risk register and privacy/license constraints.

## Artifacts

`RESEARCH-PLAN.md` orders knowledge closure. `DATA-ACQUISITION-PLAN.md` defines how public/field data enters evidence. `BENCHMARK-DESIGN.md` is the certified model-comparison protocol. `EXIT-CRITERIA.md` defines when MK0 is complete without confusing protocol readiness with empirical product performance.

## Planning principles

No test set tuning; group-aware splits; same manifest for model comparison; external gates never guessed; performance targets labeled as targets; every result bundle references code/data/model/config identity.

## Output

A complete MK0 plan yields the MK1 Definition of Ready and leaves only empirical outputs—model winner, thresholds, runtime, capacity, distance/SNR—and hardware/permission gates open.

## Invalidation

Reopen if taxonomy, model set, data policy, source contract or metric definitions materially change.