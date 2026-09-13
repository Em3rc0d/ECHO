# Quarry — Streaming / Cameras

**Status:** generic ingest architecture `CERTIFIED`; real camera `EXTERNAL_GATE_OPEN`.

## 1. Purpose

Define how continuous audio reaches ECHO reliably without coupling the core classifier to one camera vendor, RTSP path or codec.

## 2. Source abstraction

All inputs implement a common conceptual contract:

```text
SourceAdapter
  source_id
  open()
  read/decode audio
  expose timestamps/sequence where available
  health()
  reconnect()
  close()
```

Supported source types may include:

```text
RTSP_CAMERA
RTSP_NVR_CHANNEL
LOCAL_FILE_REPLAY
LOCAL_MICROPHONE (development only)
```

Downstream layers consume normalized PCM/windows, not vendor-specific URLs.

## 3. RTSP position

`DECISION`: RTSP is the primary camera ingest path for MK1 where available. FFmpeg documentation supports RTSP demuxing with RTP transport over UDP or interleaved TCP, media-type filtering and buffering/reorder controls.

Primary reference: https://ffmpeg.org/ffmpeg-protocols.html

ONVIF is optional discovery/configuration. ECHO must still accept an explicitly configured RTSP URI without requiring ONVIF.

## 4. Decode pipeline

Reference path:

```text
camera/NVR
  -> RTSP session
  -> FFmpeg process/library adapter
  -> decode source audio codec
  -> mono PCM
  -> resample to model rate (baseline 16 kHz for YAMNet path)
  -> bounded source buffer
  -> overlapping windows
```

Original codec/sample rate are recorded as metadata before normalization.

## 5. TCP vs UDP

This is an operational knob, not ideology.

- RTP/UDP can reduce transport coupling but packets can arrive out of order or be lost.
- RTP over RTSP/TCP avoids UDP loss/reordering at the network layer but head-of-line blocking can increase delay when packets are lost.

MK1 should default to a documented transport profile and benchmark alternative behavior only if the real camera/network requires it.

## 6. Audio codecs

The exact camera codec is external evidence. Common surveillance streams can expose G.711, AAC or other formats depending on vendor/profile. ECHO does not certify compatibility until FFmpeg successfully decodes the real stream.

For each source capture:

```text
codec
bitrate
sample_rate
channels
packet/stream timebase
normalization path
```

## 7. Reconnect state machine

```text
CONNECTING
 -> STREAMING
 -> STALLED/ERROR
 -> BACKOFF
 -> RECONNECTING
 -> STREAMING
```

Backoff must be bounded/exponential enough to avoid reconnect storms. A new stream session increments `stream_generation` so stale windows from the previous session can be rejected.

## 8. Stall detection

Socket connection alone is not health. Detect independently:

```text
no packets
packets but no audio track
decoder not producing samples
samples permanently silent/muted
window pipeline not advancing
```

Each has different remediation and telemetry.

## 9. Buffering and latency budget

Latency is decomposed:

```text
camera internal buffer
network/RTSP
jitter/reorder buffer
decode/resample
window accumulation
model inference
event confirmation
pub/sub delivery
```

ECHO must report components when possible; otherwise “model latency” can hide seconds of stream buffering.

## 10. Replay parity

Offline replay should use the same normalization/windowing/event path after source decode. This allows reproducible development before camera access and prevents a separate “demo path” from becoming the only tested path.

## 11. Failure tests

Required scenarios:

- invalid credentials;
- unreachable host;
- camera reboot;
- stream stall;
- packet gaps;
- decoder crash/exit;
- codec mismatch;
- audio track absent;
- reconnect storm;
- source disabled/enabled;
- process restart while event state exists.

## 12. Security boundary

RTSP/ONVIF credentials are secrets and never embedded in committed URLs. Logs must redact credentials. Command execution must avoid shell interpolation of untrusted source values.

## 13. External camera gate

To certify the professor-provided camera ECHO still needs:

```text
brand/model
audio capability
RTSP/NVR path
ONVIF support if any
audio codec/sample rate/channels
credentials mechanism
network reachability
stream concurrency limit
permission for controlled evaluation recording
```

Until then generic architecture is certified but camera-specific performance is not.

## 14. Operational evidence

Frigate's documentation demonstrates practical per-camera `audio` stream roles and FFmpeg-based camera inputs, which supports the viability of the architecture pattern without making Frigate an ECHO dependency:

- https://docs.frigate.video/configuration/cameras/
- https://docs.frigate.video/configuration/audio_detectors/
