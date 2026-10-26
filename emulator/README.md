# ECHO VMT Camera Emulator

**Status:** `MK1 LAB EMULATOR / NOT A CLAIM ABOUT VMT PRODUCTION INFRASTRUCTURE`

This stack emulates the edge behavior ECHO expects from authorized security-camera sources without requiring physical cameras.

~~~text
controlled ECHO WAV fixture / digital silence
        + synthetic H.264 video
                 ↓
          FFmpeg publisher
                 ↓
      MediaMTX RTSP server :8554
                 ↓
       future RTSPSourceAdapter
                 ↓
                ECHO
                 ↓
        echo/events over MQTT

camera lifecycle / telemetry / lab control
                 ↓
              MQTT
~~~

RTSP carries media. MQTT does **not** carry camera audio in this emulator; it carries camera state, telemetry and control. ECHO target events remain on `echo/events`.

## Start

Prerequisite: the normal ECHO MVP artifacts must exist, including `artifacts/mvp-temporal/fixtures.json` and the temporal fixture WAVs.

~~~bash
docker compose -f compose.mvp.yaml --profile emulator up -d rtsp-server vmt-camera-emulator
~~~

Host-visible RTSP endpoints:

~~~text
rtsp://127.0.0.1:8554/vmt/cam-001   negative/background
rtsp://127.0.0.1:8554/vmt/cam-002   glass_shatter
rtsp://127.0.0.1:8554/vmt/cam-003   siren
rtsp://127.0.0.1:8554/vmt/cam-004   vehicle_horn
~~~

The video track is intentionally synthetic and inexpensive. The acoustic track is the part under test.

## Verify RTSP + MQTT

~~~bash
docker compose -f compose.mvp.yaml --profile emulator run --rm --no-deps \
  vmt-camera-emulator \
  python scripts/emulator/verify_vmt_camera_emulator.py
~~~

Expected final status: `PASS`, with one video track, one audio track and retained MQTT state `ONLINE` for every configured camera.

## Observe MQTT

~~~bash
docker compose -f compose.mvp.yaml exec broker \
  mosquitto_sub -h 127.0.0.1 -p 1883 -t 'vmt/#' -v
~~~

Topics:

~~~text
vmt/emulator/status
vmt/emulator/inventory
vmt/cameras/<SOURCE_ID>/status
vmt/cameras/<SOURCE_ID>/telemetry
vmt/cameras/<SOURCE_ID>/control
~~~

Status and telemetry contain no credentials.

## Change a sound scenario while running

Example: make camera 1 emulate glass-break audio.

~~~bash
docker compose -f compose.mvp.yaml exec broker mosquitto_pub \
  -h 127.0.0.1 -p 1883 -q 1 \
  -t 'vmt/cameras/VMT-CAM-001/control' \
  -m '{"command":"set_scenario","scenario":"glass_shatter"}'
~~~

Allowed scenarios: `negative`, `glass_shatter`, `siren`, `vehicle_horn`, `silence`.

The emulator restarts only that RTSP publisher and increments `stream_generation`.

## Simulate camera/network state

Take one camera offline:

~~~bash
docker compose -f compose.mvp.yaml exec broker mosquitto_pub \
  -h 127.0.0.1 -p 1883 -q 1 \
  -t 'vmt/cameras/VMT-CAM-001/control' \
  -m '{"command":"set_online","online":false}'
~~~

Bring it back:

~~~bash
docker compose -f compose.mvp.yaml exec broker mosquitto_pub \
  -h 127.0.0.1 -p 1883 -q 1 \
  -t 'vmt/cameras/VMT-CAM-001/control' \
  -m '{"command":"set_online","online":true}'
~~~

Force a reconnect generation:

~~~bash
docker compose -f compose.mvp.yaml exec broker mosquitto_pub \
  -h 127.0.0.1 -p 1883 -q 1 \
  -t 'vmt/cameras/VMT-CAM-001/control' \
  -m '{"command":"restart"}'
~~~

## Stop

~~~bash
docker compose -f compose.mvp.yaml --profile emulator down
~~~

## Boundary

This emulator intentionally does not assert the real VMT camera model, URI layout, ONVIF behavior, credentials, codecs, network topology or MQTT conventions. Those remain external field gates. The emulator exercises ECHO's frozen source/audio abstractions with a reproducible lab approximation.
