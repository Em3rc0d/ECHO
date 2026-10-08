# ECHO Professor Demo — Scope Freeze

**Status:** `FROZEN_AFTER_ABSTENTION_V1`  
**Date:** 2026-10-08  
**Profile:** `ECHO-MVP-001`

## Purpose

Freeze the professor-demo surface after the addition of external microphone/WAV stress testing and a conservative abstention boundary.

The demo is a presentation and robustness surface for the existing three-class ECHO MVP. It is **not** the place where future taxonomy, field calibration, OOD research or production behavior is implemented.

## Included scope

The demo may show:

- controlled validation scenarios for `GLASS_SHATTER`, `SIREN` and `VEHICLE_HORN`;
- blind user WAV upload;
- ephemeral browser microphone capture;
- the real selected ECHO scorer and Temporal Event Engine;
- score-trace diagnostics for external audio;
- `NO_TARGET` when no current target is temporally confirmed;
- `UNKNOWN` when target candidates exist on uncalibrated external audio and ECHO abstains;
- MQTT publication for governed controlled scenarios;
- explicit suppression of target MQTT publication for uncalibrated external audio under `ECHO-DEMO-ABSTENTION-v1`.

## Abstention semantics

For external microphone/WAV input:

```text
audio
  ↓
real ECHO 3-class scorer
  ↓
Temporal Event Engine
  ↓
no target candidate ───────→ NO_TARGET
  ↓ target candidate(s)
UNKNOWN / ABSTAIN
  ↓
no target event published to MQTT
```

This is deliberately conservative.

`UNKNOWN` does **not** mean a learned OOD detector has proven the sound is out-of-distribution. The current diagnostic is score-trace based. A true embedding-distance or learned OOD profile remains future empirical work outside the frozen demo scope.

## Safety against demo overclaim

External input has no ground-truth label and is not field calibrated. Therefore:

- internal target candidates are shown as candidates, not accepted detections;
- candidate target events are not published to MQTT;
- score percentages are model scores, not calibrated real-world probabilities;
- external recordings are not added to train/validation/test;
- incomplete final windows are not zero-padded into repeated temporal evidence;
- at least one complete analysis window is required.

## Explicitly out of scope

The professor demo will not add:

- `SCREAM`, `GUNSHOT`, `FIRE_ALARM`, `COLLISION_IMPACT` or other new trained classes;
- a new seven-class checkpoint;
- field threshold tuning;
- a claimed production OOD detector;
- camera RTSP/ONVIF ingestion;
- persistent raw-audio storage;
- production alerting;
- new dashboard modules unrelated to demonstrating the current acoustic pipeline.

Those belong to the project roadmap and gated MVP-002/MK1/MK2 work, not this demo.

## Reopen rule

Demo scope reopens only for:

1. a bug that prevents the frozen demo from operating as specified;
2. a correctness issue that would materially misrepresent ECHO;
3. an explicit new user decision to change the demo contract.

Feature expansion by convenience or presentation polish alone is not authorized.

## Frozen demo completion criterion

The demo is considered scope-complete when the updated Docker image is locally verified to:

1. run the four controlled scenarios;
2. accept a >= analysis-window microphone recording;
3. return `NO_TARGET` when no current target is confirmed;
4. return `UNKNOWN` and suppress target MQTT publication when external target candidates exist;
5. expose score diagnostics without retaining raw audio.


## Operator documentation

The frozen demo must be launched and checked through:

```text
demo/docker-runbook/README.md
demo/docker-runbook/ARTIFACTS.md
demo/docker-runbook/VALIDATION.md
demo/docker-runbook/TROUBLESHOOTING.md
scripts/mvp/check_demo_runtime.py
```

The canonical false-positive analysis that motivated the external-audio abstention boundary is:

```text
MK1/test/FALSE-POSITIVE-ANALYSIS-2026-10-08.md
```

These documents are part of the frozen demo contract. A workaround that requires host-installed ML/runtime services or silently bypasses `UNKNOWN / NO_TARGET` is not an equivalent demo setup.
