# Ingestion Options — MK0

## RTSP/RTP

Ruta preferida para cámara IP/NVR si la fuente ofrece audio. ONVIF Profile T documenta obtención de stream URI mediante Media Profile y soporte de audio en dispositivos/clientes compatibles; la compatibilidad real debe verificarse por modelo.

## ONVIF

ONVIF no reemplaza el decoder. Sirve para descubrimiento/capabilities/perfiles/URI cuando el dispositivo es conformante. ECHO debe poder funcionar con una RTSP URI configurada manualmente aunque ONVIF no exista.

## FFmpeg

Candidato principal para MK1 por soporte de protocolos/codecs y posibilidad de extraer sólo audio. Debe encapsularse detrás de un adapter para no contaminar el core con comandos específicos.

## GStreamer

Challenger para pipelines complejos o control fino de streaming. No se incorpora a MK1 salvo que FFmpeg falle en requisitos medidos.

## Codecs relevantes

AAC y G.711 son frecuentes en vigilancia. El preprocessing de ECHO debe emitir PCM mono normalizado al sample rate requerido por el modelo, independientemente del codec de origen.

## Fallos a probar

URI inválida, auth fallida, no-audio track, codec inesperado, packet loss, jitter, stream stall, reconexión y timestamps discontinuos.