# MK1 — First Vertical Product

**Status:** `READY_NOT_STARTED` for replay/offline build  
**Upstream:** `CERT-MK0-013`, `CERT-MK1-READY-001`

## Purpose

MK1 turns certified MK0 decisions into the first complete ECHO vertical and produces empirical evidence that documentation alone cannot provide: model winner, thresholds, false-alarm profile, latency/resources, Event Engine behavior and end-to-end delivery.

## Pipeline

```text
brainstorming -> design -> arch -> plan -> build -> test
```

The build must follow frozen contracts rather than redesigning them opportunistically.

## First vertical

```text
ReplaySource / later RTSP source
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

## Real-camera branch

`EXT-CAMERA-001` remains external. Replay can certify the core architecture. Camera-specific codec, jitter, distance and field latency claims require separate field evidence.

## Completion

MK1 is certified only after build/test evidence satisfies the Definition of Done, including benchmark, calibration, streaming replay, multi-source logical tests, delivery/failure tests and known-limitations report.

## Invalidation

A material change to MK0 taxonomy, source/audio/event contracts or benchmark protocol invalidates the affected MK1 design/build evidence.