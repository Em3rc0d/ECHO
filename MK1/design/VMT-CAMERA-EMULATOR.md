# VMT Camera Emulator — Design

**Status:** `V1 FROZEN FOR LAB BUILD`

The emulator models the minimum camera-edge behavior ECHO needs, not the full physical VMT estate.

Media plane:

~~~text
controlled audio fixture + synthetic video → FFmpeg → MediaMTX → RTSP/TCP
~~~

Control/telemetry plane:

~~~text
camera emulator → MQTT retained status + periodic telemetry
operator MQTT control → per-camera restart / online state / sound scenario
~~~

RTSP is authoritative for audio/video. MQTT is authoritative only for emulator state/control. ECHO acoustic decisions remain separate.

Each logical camera preserves `source_id`, `site_id`, `rtsp_path`, scenario and a monotonically increasing `stream_generation`. No credential is emitted in telemetry.

Allowed lab scenarios: `negative`, `glass_shatter`, `siren`, `vehicle_horn`, `silence`.

The `silence` scenario exists specifically to regression-test the known zero-input baseline activation and future `NO_SIGNAL` handling.
