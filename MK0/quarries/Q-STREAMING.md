# Quarry — Streaming / Cameras

## Preguntas

- ¿La cámara real expone audio?
- ¿RTSP directo o NVR intermediary?
- ¿ONVIF disponible?
- ¿codec/sample-rate/channels?
- ¿TCP vs UDP?
- ¿cuánto buffering añade el device?
- ¿cuántas conexiones simultáneas tolera?
- ¿necesitamos go2rtc?

## Patrón candidato

```text
RTSP -> FFmpeg -> decoded PCM -> normalize -> bounded per-source ring buffer
```

## Failure modes a probar

```text
network loss
credential failure
codec change
camera reboot
packet gaps
stalled stream
clock jump
reconnect storm
```

Estado: `EXTERNAL_GATE_OPEN` para la cámara real; `IN_PROGRESS` para diseño genérico.