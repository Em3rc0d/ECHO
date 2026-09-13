# Anti-Scope — MK0

ECHO no debe convertirse en un sistema genérico de videovigilancia.

## Fuera del core

- reconocimiento facial o identificación de personas;
- inferencia de delitos («robo», «asalto») desde audio;
- análisis semántico de conversaciones;
- seguimiento visual;
- mapas, GIS o despacho operativo como función principal;
- almacenamiento continuo de audio como requisito por defecto;
- dependencia obligatoria de cloud para la PoC;
- entrenamiento de un foundation model desde cero.

## Regla semántica

ECHO puede afirmar `GLASS_BREAK`, `SIREN`, `HORN`, `IMPACT` o una categoría acústica validada. No debe transformar automáticamente esa observación en una conclusión causal no demostrada.

## Infraestructura de soporte

RTSP/ONVIF, FFmpeg/GStreamer, MQTT, dashboard, API, base de datos y notificaciones son medios para capturar, procesar o distribuir eventos; no cambian la promesa del proyecto.