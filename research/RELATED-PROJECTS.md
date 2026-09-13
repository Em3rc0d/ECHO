# Related Projects and Comparable Systems

**Status:** `MK0_CERTIFIED_LANDSCAPE / CONTINUOUSLY EXTENDABLE`

## Purpose

Identify which ECHO components are already solved by the ecosystem, validate operational patterns and clarify where ECHO's own engineering/research contribution remains. Related projects are references, not templates to copy blindly.

## Frigate NVR

Relevant features documented by the project include IP-camera processing, FFmpeg/go2rtc integration patterns, per-camera audio detection and MQTT integration. ECHO learns that camera-scoped audio event processing and Pub/Sub are operationally realistic. Difference: Frigate is a broader NVR, whereas ECHO focuses on an independently benchmarked/certified acoustic detection/classification layer and its evidence pipeline.

Primary docs: https://docs.frigate.video/configuration/audio_detectors/ and https://docs.frigate.video/integrations/mqtt/

## YAMNet real-time detectors

Open projects using microphone/stream input with YAMNet show that continuous short-window classification and selected-class notification are practical. Many are useful PoCs but do not necessarily include rigorous data governance, group-aware splits, source-hour false-positive evaluation, multi-source scheduling or event lifecycle semantics.

## IP-camera / RTSP audio monitors

Projects such as specialized cry/baby sound monitors demonstrate a concrete path `RTSP -> audio extraction -> model -> notification`. ECHO uses them as feasibility evidence while retaining different target taxonomy, privacy context, Event Engine and multi-source goals.

## Acoustic localization systems

Research/open implementations combine sound-event detection with microphone arrays and direction-of-arrival. They show a future extension path but are outside the fixed current scope because direction estimation is not required to detect/classify events.

## Sensor-network research

SONYC and DCASE-related urban SED work provide stronger evidence for real ambient sound, multilabel/polyphony and site/domain variation than small curated clip projects. They influence ECHO evaluation design more than application architecture.

## Commercial camera analytics

Vendor/NVR products may expose audio anomaly classes, proving market relevance but offering limited visibility into models/training/evaluation. They are not acceptable scientific evidence for ECHO quality.

## Comparison framework

For each system record source type/protocol; audio preprocessing; model; label semantics; continuous/temporal aggregation; multi-source behavior; event API/PubSub; hardware; licensing; maintenance; privacy; known limitations.

## What ecosystem already solves

RTSP decoding, broker messaging, pretrained audio representations and basic camera supervision are existing building blocks. ECHO does not claim novelty for them.

## ECHO-specific value

Versioned source/audio/event contracts; controlled target taxonomy; asset-level data governance; comparative model selection; continuous false-alarm/latency evidence; temporal Event Engine; multi-source capacity/failure testing; and chained evidence/certification.

## Invalidation

Update when a new directly comparable open system materially changes assumptions or offers a component whose adoption would simplify ECHO without violating scope.