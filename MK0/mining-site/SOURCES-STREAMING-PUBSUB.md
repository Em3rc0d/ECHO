# Streaming and Pub/Sub Sources — MK0

**Status:** `CERTIFIED_LANDSCAPE`

## Purpose

Preserve authoritative sources that justify the ingest and event-delivery design without confusing standard capability with actual-device support.

## ONVIF

Profile T/media specifications support interoperable media profiles and audio capabilities where implemented. ECHO uses ONVIF as optional discovery/configuration evidence. The actual camera's support remains a hardware gate.

## RTSP / FFmpeg

FFmpeg protocol/format documentation establishes RTSP transport and decoding options used by the baseline adapter. Exact codec support depends on the binary/build; ECHO records runtime version/config.

## GStreamer

`rtspsrc` and related elements expose jitter/latency/transport controls useful when camera behavior requires finer pipeline management. GStreamer remains a fallback/challenger.

## MQTT 5.0

OASIS specification defines QoS/session/topic semantics. QoS1 is at-least-once, motivating `event_id` idempotency. Retained messages represent last-known retained publication behavior, not a durable event-history substitute.

## Eclipse Mosquitto

Official project documentation establishes the lightweight broker used for MK1 local/self-hosted event routing.

## Related system: Frigate

Frigate documentation shows per-camera audio detection and MQTT integration in an open-source NVR. It is used as operational precedent for the pattern, not as evidence of ECHO accuracy or architecture identity.

## Validation boundary

Standard documentation certifies feasible interfaces; actual packet loss, codec, jitter, connection limits, broker performance and camera firmware behavior require ECHO tests.

## Source hygiene

Pin protocol/spec versions where relevant and record accessed docs in the web audit/reference catalog.