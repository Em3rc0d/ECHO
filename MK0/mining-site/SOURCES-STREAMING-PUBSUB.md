# Sources — Streaming & Pub/Sub

## ONVIF Profile T

Profile T cubre streaming IP y audio bidireccional cuando el dispositivo/cliente soporta esas capacidades. La especificación describe `GetProfiles`/`GetStreamURI`, RTSP y codecs de audio como G.711 μ-law y AAC para conformidad condicional de audio.

- https://www.onvif.org/profiles/profile-t/
- https://www.onvif.org/wp-content/uploads/2018/09/ONVIF_Profile_T_Specification_v1-0.pdf

## FFmpeg

Documentación oficial de protocolos/demuxers se usa para validar RTSP/RTP y opciones de transporte. ECHO no debe codificar una ruta RTSP de fabricante como estándar universal.

- https://ffmpeg.org/ffmpeg-protocols.html

## MQTT 5

OASIS define QoS 0 `at most once`, QoS 1 `at least once`, QoS 2 `exactly once` a nivel de protocolo. Para ECHO MK1 se considera QoS 1 + `event_id` idempotente; la durabilidad end-to-end requiere configuración adicional del broker/cliente.

- https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html

## Frigate benchmark arquitectónico

Frigate expone detección de audio por cámara y múltiples topics MQTT. Sirve como prueba de patrón, no como especificación de ECHO.

- https://docs.frigate.video/configuration/audio_detectors/
- https://docs.frigate.video/integrations/mqtt/