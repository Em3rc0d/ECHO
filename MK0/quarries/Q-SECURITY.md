# Quarry — Security

## Superficies

RTSP credentials, ONVIF credentials, broker auth, API, model/checkpoint supply chain, config files, logs y archivos de audio.

## Preguntas

- ¿cómo inyectar secretos sin Git?
- ¿TLS disponible en cámara/broker y qué hacer si RTSP sólo viaja en LAN?
- ¿qué ACL impide que un publisher publique como otra cámara?
- ¿cómo evitar path/command injection en adapters FFmpeg?
- ¿cómo validar modelos/checkpoints por checksum?
- ¿cómo registrar intentos/reconnect sin filtrar passwords en logs?

## Principio

La PoC local puede aceptar una red de laboratorio confiable, pero debe documentar explícitamente qué controles se difieren a MK2.