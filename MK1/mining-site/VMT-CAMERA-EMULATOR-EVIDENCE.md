# VMT Camera Emulator — Mining Site

**Status:** `ACTIVE LAB EVIDENCE`

## Provenance

The emulator reuses ECHO's governed temporal fixture WAVs already present under the local artifact store. Those files are not copied into Git. A fifth scenario, `silence`, is generated locally with FFmpeg and contains digital silence.

The RTSP server is MediaMTX, pinned in Compose to `bluenviron/mediamtx:1.21.3`. Media is published by the FFmpeg binary already installed in the existing ECHO MVP image.

## What this evidence can prove

- multiple independent RTSP paths can exist simultaneously;
- ECHO's Docker environment can publish/read H.264 + AAC RTSP media;
- per-source lifecycle and reconnect generations can be exercised;
- MQTT retained status and periodic telemetry can be exercised;
- controlled acoustic fixtures can traverse a camera-like transport path.

## What it cannot prove

- compatibility with the actual VMT camera/NVR model;
- actual VMT RTSP URI/profile, codec, microphone quality or ONVIF behavior;
- VMT network latency, packet loss, firewall/VPN behavior or concurrency limits;
- field false-alarm performance;
- actual VMT MQTT conventions, if any.

Those remain external gates and must be measured on authorized infrastructure.
