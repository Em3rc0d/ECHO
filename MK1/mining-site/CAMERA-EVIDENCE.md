# MK1 Camera Evidence

**Status:** `EXTERNAL_GATE_OPEN`

## Purpose

Store sanitized evidence that the professor-provided camera/NVR can serve as a valid ECHO source and characterize the domain it introduces.

## Required identity

Brand/model, firmware if available, microphone/audio capability, NVR intermediary if any, physical mounting/site context and authorization record. Credentials are never stored here.

## Probe evidence

RTSP/ONVIF support, chosen stream/profile, audio codec, sample rate/channels/bitrate, transport behavior, FFmpeg/GStreamer probe output sanitized of secrets and simultaneous connection observations.

## Stability evidence

Connection duration, stalls/gaps, reconnect after interruption/reboot, decoder errors, observed buffering and source health telemetry.

## Acoustic evidence

Signal levels/noise, AGC/noise suppression effects if observable, safe target/negative tests, distance/SNR metadata and model/event results on untouched field subset.

## Closure

Only executed field evidence changes status from `EXTERNAL_GATE_OPEN`. Documentation for a similar camera model is insufficient.

## Invalidation

Firmware, camera/NVR, network or site change can invalidate compatibility/performance claims.