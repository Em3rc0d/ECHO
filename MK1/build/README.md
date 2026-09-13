# MK1 / Build

**Status:** `IN_PROGRESS — DATA_FOUNDRY_FOUNDATION_PASS`

## Purpose

Materialize the certified first vertical without reopening closed design choices in code. Build is execution of contracts and experiment protocols, not a new brainstorming phase.

## Entry gate

`CERT-MK1-READY-001` authorizes replay/offline implementation. Real-camera code can be added when `EXT-CAMERA-001` provides enough hardware/access evidence.

## Current build position

The first concrete MK1 build increment is the **Data Foundry**. Its role is to turn heterogeneous external/field sources into reproducible, license-aware, semantically mapped, group-safe manifests before any model benchmark is allowed to consume data.

```text
MK1/build
  Data Foundry foundation     PASS
  corpus acquisition/admit    IN_PROGRESS / EMPIRICAL
  replay/audio pipeline       NEXT AFTER FROZEN CORPUS INPUTS
  model runners A/B/C         GATED BY DATA HANDOFF
  Event Engine                LATER
  MQTT/persistence            LATER
```

Detailed Foundry artifacts live in `MK1/build/data-foundry/`. Machine-readable policies live in `configs/data_foundry/`, schemas in `schemas/data_foundry/`, implementation in `src/echo/data_foundry/`, and tests in `tests/data_foundry/`.

## Foundry foundation evidence

`CERT-MK1-DF-SPEC-001` covers the current Foundry architecture/contracts/policies and deterministic code foundation. GitHub Actions run `34741450390` passed on Python 3.10, 3.11 and 3.12; the 3.11 job ran 23 unit tests successfully. See `MK1/test/DATA-FOUNDRY-FOUNDATION.md`.

The certificate deliberately does **not** claim that a final corpus exists. `EMP-DATASET-001` and `EMP-DATA-QUALITY-001` remain open until source releases are acquired, assets are hashed/admitted/reviewed and split/dedup reports are generated.

## Expected remaining modules

After the Foundry handoff: Source/replay adapters, audio normalization/windowing, model-runner interfaces and A/B/C implementations, EventEngine, MQTT publisher/subscriber, minimal structured persistence/query, observability and benchmark/test tooling.

## Build evidence

Every build/run records commit, dependency lock, config, model/checkpoint, data manifest and schema versions. Product code must not hardcode credentials, source count or model thresholds as unexplained constants.

## Rule

If implementation discovers a missing architecture-changing decision, stop and reopen the upstream artifact instead of hiding it in code. Data leakage, unknown rights, ambiguous positive label mapping or unbounded/mutable corpus selection are stop-the-line failures.

## Output

A reproducible vertical ready for `MK1/test`, not a release claim.