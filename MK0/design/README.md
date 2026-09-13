# MK0 / Design

**Status:** `CERTIFIED_INPUT_TO_ARCH`

## Purpose

Design converts the broad problem landscape into a bounded product definition: what inputs/outputs exist, which acoustic labels are candidates, what non-functional qualities matter and which semantics must remain stable independent of implementation technology.

## Inputs

MK0 brainstorming, dataset/model research, related-system evidence and the fixed project charter.

## Artifacts

- `SYSTEM-BOUNDARY.md` defines ownership and interfaces.
- `TAXONOMY-CANDIDATES.md` explains the path from broad candidate labels to the frozen MK1 v1 taxonomy.
- `NONFUNCTIONAL-DRIVERS.md` defines qualities that drive architecture and tests.

## Key invariant

Design does not encode camera count, Python process topology or broker implementation into domain semantics. `source_id`, audio windows, inference records and events remain stable even when deployment topology changes.

## Exit condition

Architecture can proceed when responsibilities, data semantics, privacy boundary and quality drivers are explicit enough that component boundaries can be derived without guessing.

## Invalidation

Revisit if taxonomy semantics, product boundary, source/audio contract or major quality priorities change.