# MK1 / Build

**Status:** `READY_NOT_STARTED`

## Purpose

Materialize the certified first vertical without reopening closed design choices in code. Build is execution of contracts and experiment protocols, not a new brainstorming phase.

## Entry gate

`CERT-MK1-READY-001` authorizes replay/offline implementation. Real-camera code can be added when `EXT-CAMERA-001` provides enough hardware/access evidence.

## Expected modules

Source/replay adapters, audio normalization/windowing, model-runner interfaces and A/B/C implementations, EventEngine, MQTT publisher/subscriber, minimal structured persistence/query, observability and benchmark/test tooling.

## Build evidence

Every build/run records commit, dependency lock, config, model/checkpoint, data manifest and schema versions. Product code must not hardcode credentials, source count or model thresholds as unexplained constants.

## Rule

If implementation discovers a missing architecture-changing decision, stop and reopen the upstream artifact instead of hiding it in code.

## Output

A reproducible vertical ready for `MK1/test`, not a release claim.