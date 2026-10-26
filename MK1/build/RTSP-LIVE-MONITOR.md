# ECHO Live Camera Monitor — MK1 experimental slice

This feature is intentionally on a review branch until validated on the Docker host.
It reads four emulator RTSP tracks through FFmpeg (audio only), decodes mono
float32 PCM at the selected scorer sample rate, builds **complete 6-second
windows with a 1-second hop**, runs the selected PANNs/ECHO head and the
existing TemporalEventEngine, and writes bounded, atomic JSON snapshots for UI.

No intermediate WAV is written. Audio samples are held only in memory.
Each source gets a separate temporal engine and new worker session on reconnect.
The worker serializes model scoring with a lock to protect the shared model.

## Run

```bash
git fetch origin
git switch feat/rtsp-live-monitor-mk1

docker compose -f compose.mvp.yaml --profile demo --profile emulator --profile live \
  up -d --build broker consumer demo rtsp-server vmt-camera-emulator echo-rtsp-worker

docker compose -f compose.mvp.yaml logs -f echo-rtsp-worker
```

Open **http://localhost:8088/live**.

Check source diagnostics:

```bash
docker compose -f compose.mvp.yaml --profile live exec echo-rtsp-worker \
  cat /workspace/artifacts/live-monitor/VMT-CAM-002.json
```

**Boundaries:** The new RTSP source path is diagnostic-only. Candidate events
are shown but *not* published as accepted targets on `echo/events` pending
validation against codec/domain confusers and robustness gate #53. The UI
only displays a sampled audio envelope (not an audio player), and video remains
viewable in VLC; RTSP is not natively playable in most browsers. The worker
session counter is local to the worker and is **not** the emulator's
MQTT `stream_generation`; MQTT generation reconciliation remains follow-up work.

Acceptance before merging: run Docker smoke test, confirm four sources each
reach ONLINE, confirm scores and waveform change with `set_scenario`, prove
disconnection/restart resets temporal sessions, verify controlled negative
does not create accepted events, and run CPU/latency stress tests.

## Browser audiovisual + MQTT camera-control increment (2026-10-26)

The live view embeds MediaMTX's HLS player at `http://127.0.0.1:8888/vmt/cam-00N/`.
MediaMTX HLS listens on localhost only; this is a local-demo design,
not a remotely secured deployment. Open `http://localhost:8088/live`,
select the camera and enable playback/audio in the embedded player.
Audio/video and inference data are separate paths and may not be frame-synchronized.

The `/api/live/control` POST endpoint permits only four fixed camera IDs,
`set_scenario` (five allowed scenarios), `set_online` (boolean),
and `restart`, then sends MQTT QoS1. An accepted publish means broker
delivery, **not camera acknowledgement**. The UI still shows diagnosis-only
temporal candidates and NEVER publishes accepted `echo.event.v1`.

Recreate MediaMTX (new HLS port/config), demo (new HTTP handler),
and the worker:

```bash
git pull --ff-only origin feat/rtsp-live-monitor-mk1
docker compose -f compose.mvp.yaml --profile emulator --profile demo --profile live \
  up -d --build --force-recreate rtsp-server vmt-camera-emulator echo-rtsp-worker demo
docker compose -f compose.mvp.yaml --profile emulator --profile demo --profile live \
  ps
```

Visit `http://localhost:8088/live`. To verify MediaMTX HLS:
`curl -I http://127.0.0.1:8888/vmt/cam-002/index.m3u8`.
Some HLS variants/browser players use alternate playlist requests: inspect the
MediaMTX browser page directly if required.

**Still needs real Docker/browser verification:** HLS playback with audio,
switching scenes while preserving inference, reconnect/worker generation,
browser console / CSP checks, and security regression on command endpoints.
