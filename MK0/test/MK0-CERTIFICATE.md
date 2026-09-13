# MK0 Certificate

**Certificate ID:** `CERT-MK0-013`  
**Status:** `CERTIFIED`  
**Scope:** research/design/architecture/plan readiness for MK1 replay build.

## Certified statements

- ECHO's immutable promise and observable-event boundary are explicit.
- A multi-source logical architecture is defined independent of physical camera count.
- RTSP source abstraction, FFmpeg baseline and optional ONVIF/GStreamer path are defensible.
- The MK1 v1 taxonomy and multi-label semantics are frozen.
- Public-data use is governed by provenance/license/group-aware split rules.
- A/B/C benchmark protocol is frozen before model selection.
- Raw inference, candidate event, confirmed event and alert semantics are separated.
- MQTT/Mosquitto + QoS1/idempotency is the MK1 delivery baseline.
- Privacy/security baseline and external camera gate are explicit.

## Not certified

This certificate does not assert model accuracy, model winner, thresholds, real-camera compatibility, distance, latency, source capacity or final SLOs. Those are empirical/external outputs.

## Evidence inputs

MK0 brainstorming/design/arch/plan artifacts, mining-site source audit, quarries, research matrices, risk register, privacy/license controls and `MK0-GATE.md`.

## Dependency behavior

A material taxonomy change invalidates data mappings/benchmark/event consumers but not necessarily RTSP evidence. A source-protocol change affects ingestion certificates without automatically invalidating model/data research. Dependency-specific invalidation follows the certification DAG.

## Handoff

The certificate authorizes `CERT-MK1-READY-001` for replay/offline build while `EXT-CAMERA-001` remains open.

## Historical integrity

The certificate is versioned through Git; future recertification creates a new active version rather than erasing this record.