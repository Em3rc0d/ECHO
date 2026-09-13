# MK1 / Plan

**Status:** `CLOSED_FOR_BUILD`

## Purpose

Order the first implementation and experiments so evidence remains comparable and the team does not tune the system against the final test set.

## Sequence

Data manifest/splits -> replay/audio core -> A/B/C model arms -> validation/calibration -> EventEngine -> streaming replay -> MQTT/E2E -> multi-source/fault tests -> real-camera branch -> MK1 certification.

## Artifacts

Benchmark, data, training, evaluation, integration, field-test, implementation sequence and rollback plans describe this order in detail.

## Scientific rule

Model and event parameters are chosen with train/validation evidence; test/field holdout is used only for final evaluation. Changing data/taxonomy after seeing test results creates a new benchmark version.

## Operational rule

Every phase produces artifacts that can be replayed/recomputed before the next phase claims success.

## Invalidation

Any upstream contract/manifest change requires recomputing dependent plan outputs/results.