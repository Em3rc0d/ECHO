# Anti-Scope — What ECHO Must Not Become

**Status:** `CERTIFIED_BOUNDARY`

## Purpose

Anti-scope protects the fixed product promise from attractive but architecture-expanding features. A feature may be useful and still not belong to ECHO core.

## Excluded interpretations

ECHO does not infer crimes, intent, emergencies, identity or causality solely from audio. `GLASS_SHATTER` is an acoustic class; `ROBBERY` is a contextual incident. `SIREN` is a sound; `EMERGENCY` is a situation.

## Excluded product expansions for MK1/MK2 core

- facial/person recognition;
- generic video analytics;
- speech-to-text and conversation understanding;
- speaker identification/biometrics;
- autonomous law-enforcement decisions;
- a full NVR replacement;
- a generic smart-city platform;
- maps/patrol optimization unrelated to acoustic detection;
- blockchain/token/consensus infrastructure;
- acoustic source localization requiring microphone arrays unless separately proposed later.

## Support components that are allowed

Cameras, RTSP/ONVIF, relays, MQTT, storage, APIs, dashboards and notifications are acceptable when they support the acoustic pipeline. They must remain replaceable and must not redefine the project.

## Scope-change test

Ask:

```text
Does this capability directly improve or operationalize detection/classification
of acoustic events by AI?
```

If no, it is downstream/integration work or another product. If yes but it changes the fixed promise, it still requires charter-level review.

## Why this matters

Uncontrolled scope would dilute training data, metrics and architecture, make the academic claim impossible to evaluate and create privacy/security obligations unrelated to the core thesis.

## Invalidation

Only an explicit owner decision to create a new product/scope can override this file. A professor integration request is not automatically a promise change.