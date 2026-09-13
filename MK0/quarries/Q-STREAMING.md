# Quarry — Streaming / Cameras

**Status:** `GENERIC_ARCH_CERTIFIED / REAL_CAMERA_EXTERNAL`

## Questions resolved architecturally

ECHO accepts source adapters instead of coupling to a camera vendor. RTSP is the primary IP-camera transport path; ONVIF discovery/config is optional; FFmpeg is the baseline decoder; GStreamer is fallback/challenger.

## Unknowns that require the actual device

Audio availability, exact RTSP URI/profile, codec/sample rate/channels, AGC/noise suppression, TCP/UDP behavior, buffering, simultaneous client limits, firmware quirks, network/NAT/firewall and credentials.

## Reference path

```text
SourceSupervisor
 -> connect/probe
 -> RTSP demux/decode
 -> normalized PCM
 -> bounded ring buffer
 -> windows
```

Each connection has a `stream_generation`; old-generation windows are rejected after reconnect.

## Health states

```text
DISABLED -> CONNECTING -> ONLINE -> DEGRADED
-> RECONNECTING -> ONLINE/OFFLINE
```

Track packet/decode freshness, last sample/window, buffer fill, queue lag, reconnect count and decode errors. Connected-but-muted audio needs a separate signal-quality warning.

## Failure tests

Credential rejection, no audio track, unsupported codec, packet loss, stalled stream, camera reboot, clock jump, decode crash and reconnect storm. Other sources must continue when one fails.

## Transport trade-off

TCP can reduce loss at cost of head-of-line latency; UDP may reduce latency but tolerate loss. No transport is globally frozen before the camera/network test.

## Security

RTSP credentials are injected via secret references and redacted from commands/logs. If transport is unencrypted, field deployment must constrain network trust/segmentation or provide secure tunneling as applicable.

## Validation

Replay validates downstream contracts. Real camera closes `EXT-CAMERA-001` with sanitized probe logs, stability/reconnect evidence and measured signal/latency characteristics.

## Invalidation

If standards-based access fails, add a vendor/NVR/mic adapter while preserving downstream source/audio contracts.