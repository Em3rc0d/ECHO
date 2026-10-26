# VMT Camera Emulator — Build Record

**Status:** `SOURCE IMPLEMENTED / DOCKER EXECUTION PENDING`

Implemented components:

- `docker/emulator/mediamtx.yml` — RTSP server configuration;
- `config/emulator/vmt-cameras.json` — four logical camera definitions;
- `scripts/emulator/vmt_camera_emulator.py` — FFmpeg publishers + per-camera lifecycle + MQTT telemetry/control;
- `scripts/emulator/verify_vmt_camera_emulator.py` — RTSP/MQTT smoke verifier;
- `emulator/README.md` — operator runbook;
- `compose.mvp.yaml` profile `emulator` — local Docker orchestration.

MediaMTX is pinned to `bluenviron/mediamtx:1.21.3`. The ECHO emulator itself runs in the existing `echo-mvp:local` image and therefore uses the same Docker FFmpeg/runtime boundary as the MVP.

No real VMT credential, camera address or private network information is committed.
