# Source Contract — MK1

## SourceDescriptor

```yaml
source_id: CAM-01
kind: rtsp
site_id: LAB-01
enabled: true
uri_secret_ref: echo/cam01/rtsp
transport_preference: tcp
audio_required: true
metadata:
  location_label: corridor-a
```

## Source states

`DISABLED -> CONNECTING -> HEALTHY -> DEGRADED -> RECONNECTING -> HEALTHY` o `FAILED`.

## Invariantes

- `source_id` estable y único;
- URI/credentials nunca aparecen en eventos ni logs;
- un source defectuoso no bloquea otros;
- adapters implementan la misma interfaz para `file`, `microphone`, `rtsp`;
- health incluye `last_audio_ts`, reconnect count, decode errors y buffer depth.

## External gate

Campos específicos de cámara (modelo, codec, RTSP path, ONVIF) se completan sólo con evidencia real.