# Ingestion Options — MK0

**Status:** `RTSP+FFMPEG_BASELINE_CERTIFIED / CAMERA_EXTERNAL`

## 1. Requirement

ECHO needs a source adapter that emits normalized acoustic samples plus source/timing metadata. Physical acquisition may come from IP camera, NVR, microphone or replay file.

## 2. IP-camera path

Primary candidate:

```text
camera/NVR -> RTSP/RTP -> FFmpeg -> decoded PCM -> normalization
```

ONVIF is useful for discovery/profile/configuration but is not required when an RTSP URI is explicitly configured. The actual professor-provided camera remains an external gate.

## 3. Decoder alternatives

### FFmpeg

Selected MK1 baseline because of broad codec/RTSP support, simple subprocess/library integration and mature diagnostics. Exact build/version must be recorded because codec availability and licensing vary.

### GStreamer

Strong alternative when the project needs finer streaming pipeline control, jitter behavior, dynamic reconnection or plugin-oriented composition. It is retained as a fallback/challenger, not a mandatory dependency.

### go2rtc/NVR relay

Useful for stream fan-out or normalizing camera quirks, but adds another process/config layer. It is optional and introduced only if hardware evidence justifies it.

## 4. Normalized audio contract

Baseline model research assumes mono normalized PCM at a defined sample rate (16 kHz for the YAMNet path). Original codec/sample rate/channels remain metadata so codec/domain effects can be audited.

## 5. Timing/source metadata

Each decoded stream/session carries `source_id`, `stream_generation`, sequence/media timestamps when reliable and receive time. Reconnect creates a new generation so stale windows from a prior stream cannot contaminate current event state.

## 6. Failure modes

Credential failure, unsupported codec, no audio track, packet loss, stalled stream, camera reboot, time jump, decode process crash and reconnect storms require explicit health state/telemetry.

## 7. Alternatives rejected as core assumption

Direct vendor SDK lock-in is avoided unless the actual hardware makes standards-based access impossible. Browser/WebRTC ingest is not required for the first backend acoustic pipeline.

## 8. Validation

Offline replay validates adapter contract. Real camera validation probes codec, stream stability, TCP/UDP behavior, reconnect, silence/mute detection and end-to-end timing.

## 9. Invalidation

If real hardware exposes no usable RTSP/audio, retain the source contract and add a vendor/NVR/external-mic adapter rather than rewriting downstream inference.