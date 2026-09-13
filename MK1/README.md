# MK1 — First Vertical Product

**Status:** `BUILD_IN_PROGRESS — DATA FOUNDRY FOUNDATION CERTIFIED`  
**Upstream:** `CERT-MK0-013`, `CERT-MK1-READY-001`

## Purpose

MK1 turns certified MK0 decisions into the first complete ECHO vertical and produces empirical evidence that documentation alone cannot provide: model winner, thresholds, false-alarm profile, latency/resources, Event Engine behavior and end-to-end delivery.

## Pipeline

```text
brainstorming -> design -> arch -> plan -> build -> test
```

The build follows frozen contracts rather than redesigning them opportunistically.

## Current position

```text
brainstorming  CLOSED_FOR_BUILD
     ↓
design         CLOSED_FOR_BUILD
     ↓
arch           CLOSED_FOR_BUILD
     ↓
plan           CLOSED_FOR_BUILD
     ↓
build          IN_PROGRESS
  ├── Data Foundry foundation     CERTIFIED
  └── corpus execution            OPEN
     ↓
test           foundation evidence PASS; full MK1 test pending
```

The Data Foundry is the first build increment because model comparison is meaningless without a frozen, provenance/rights-aware and leakage-resistant data identity.

## First vertical

```text
Frozen Foundry manifest
 -> ReplaySource / later RTSP source
 -> decode + normalize
 -> bounded source buffer
 -> windows
 -> A/B/C model runner
 -> RAW_INFERENCE
 -> temporal Event Engine
 -> CONFIRMED_EVENT
 -> MQTT
 -> subscriber / persistence / query
```

## Scope

MK1 targets the v1 acoustic taxonomy, multi-label scoring, deterministic replay, source identity, temporal aggregation, Pub/Sub and measurable quality/runtime. It does not need production-scale distributed workers, unlimited cameras, advanced OOD or final cloud operations.

## Data Foundry status

The foundation now includes versioned source registry, label mapping, rights/admission policy, JSON schemas, group-aware split primitives, manifest hashing, dataset metadata adapters, hard-negative plan, field-holdout design and CI-tested code. Actual source archives/admitted asset counts remain empirical and are not fabricated.

## Real-camera branch

`EXT-CAMERA-001` remains external. Replay can certify the core architecture. Camera-specific codec, jitter, distance and field latency claims require separate field evidence.

## Completion

MK1 is certified only after build/test evidence satisfies the Definition of Done, including data/corpus gates, benchmark, calibration, streaming replay, multi-source logical tests, delivery/failure tests and known-limitations report.

## Invalidation

A material change to MK0 taxonomy, source/audio/event contracts, benchmark protocol or Foundry corpus semantics invalidates the affected MK1 design/build evidence.