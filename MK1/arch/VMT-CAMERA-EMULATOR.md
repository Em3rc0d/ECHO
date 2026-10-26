# VMT Camera Emulator — Architecture

**Status:** `IMPLEMENTED_REFERENCE`

~~~text
                         ┌────────────────────────────┐
                         │ Mosquitto                  │
                         │ vmt/cameras/...            │
                         │ status/telemetry/control   │
                         └─────────────┬──────────────┘
                                       │ MQTT QoS 1
┌──────────────────────┐     ┌─────────▼──────────────┐
│ Governed ECHO audio  │────▶│ vmt-camera-emulator   │
│ fixtures / silence   │     │ per-camera supervisor │
└──────────────────────┘     └─────────┬──────────────┘
                                       │ FFmpeg publishers
                                       ▼
                              ┌───────────────────────┐
                              │ MediaMTX              │
                              │ RTSP/TCP :8554        │
                              └──────────┬────────────┘
                                         │
                                         ▼
                              future RTSPSourceAdapter
                                         │
                                         ▼
                                        ECHO
                                         │
                                         ▼
                                   echo/events MQTT
~~~

MediaMTX is the RTSP server because it accepts FFmpeg RTSP publishers and exposes multiple independent paths. The emulator process owns per-camera FFmpeg lifecycle and stream generations. A camera publisher failure is source-scoped and reconnects with bounded delay.

The architecture deliberately matches `SOURCE-CONTRACT.md`: changing a replay source to an RTSP source must not change downstream event semantics.
