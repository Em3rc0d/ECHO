# VMT Camera Emulator — Test Gate

**Status:** `STATIC PASS / DOCKER RUNTIME PENDING`

Automated verifier requirements per configured camera:

- retained MQTT status received;
- status is `ONLINE`;
- RTSP URI is reachable over TCP;
- at least one video track exists;
- at least one audio track exists;
- verifier reports codec/sample-rate evidence.

Additional manual controls to exercise:

- `set_scenario` changes only one camera and increments stream generation;
- `set_online=false` makes that camera unavailable without taking down the others;
- `set_online=true` reconnects it;
- `restart` produces a new stream generation;
- `silence` remains an explicit source-quality regression case.

The source files were Python syntax-compiled and fixture resolution was tested with synthetic fixture metadata before commit. Full Docker/MediaMTX execution must be run on the user host; repository-side source inspection is not equivalent to runtime evidence.
