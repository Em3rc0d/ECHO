# VMT Camera Emulator — Brainstorming

**Status:** `SELECTED_FOR_MK1_BUILD`

Goal: unblock camera-path engineering before authorized VMT hardware/network access is available.

Selected idea: emulate multiple security cameras as independent RTSP publishers with MQTT lifecycle, telemetry and control. Reuse governed ECHO acoustic fixtures so media provenance remains known. Keep the emulator outside the frozen professor-demo semantics.

Rejected shortcuts: sending WAV payloads through MQTT; hard-coding ECHO predictions; pretending a silent public RTSP demo feed represents field audio; exposing Mosquitto publicly; inventing actual VMT credentials or topology.

Success means a downstream client can swap `ReplaySource` for the emulator RTSP URI while preserving source identity, stream generation and acoustic-processing contracts.
