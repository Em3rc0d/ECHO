# Q-VMT-CAMERA-EMULATOR

**Status:** `OPEN / LAB-FIRST`

Question: can ECHO's frozen source/audio contracts survive the transition from deterministic replay to camera-like RTSP streams without changing downstream acoustic-event semantics?

## Lab questions

- Does each source remain isolated when another RTSP publisher restarts or goes offline?
- Does `stream_generation` prevent stale temporal state from leaking across reconnects?
- Can the future live adapter maintain 6 s windows / 1 s hop under real-time delivery?
- What freshness/drop policy is needed when inference falls behind?
- Does the Signal Quality Gate correctly distinguish `NO_SIGNAL` from `NO_TARGET`?
- Do the controlled glass/siren/horn fixtures remain detectable after AAC encode/decode?
- Does target-free fixture audio remain target-free after the RTSP codec path?

## Field questions kept open

Exact VMT camera model, firmware, RTSP profile, audio codec/rate/channels, ONVIF capability, authentication, network reachability, concurrent-reader limits, microphone processing and safe test conditions remain unknown until authorized field evidence is available.
