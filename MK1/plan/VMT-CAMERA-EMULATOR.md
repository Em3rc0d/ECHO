# VMT Camera Emulator — Plan

**Status:** `V1 BUILT / RUNTIME VALIDATION PENDING ON USER HOST`

1. Add a pinned MediaMTX RTSP server to the Docker-only stack.
2. Add four configured logical cameras using governed temporal fixtures.
3. Publish camera lifecycle and telemetry to Mosquitto.
4. Accept safe lab control commands over MQTT: restart, online/offline and scenario switch.
5. Add an RTSP+MQTT verification script.
6. Run the stack on the developer host and prove every stream has video + audio and every camera reaches `ONLINE`.
7. Next, implement `RTSPSourceAdapter` against these URIs and test source reconnect/generation handling.
8. Only after emulator closure, swap one emulator URI for an authorized real camera URI without downstream changes.
