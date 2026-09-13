# Scope Cut — MK1

## IN

- ingestión desde archivo/replay y una cámara/NVR si el external gate se resuelve;
- normalización a contrato de audio;
- clasificación de una taxonomía ECHO pequeña y versionada;
- inferencia por ventanas;
- Event Engine temporal;
- publicación de eventos confirmados;
- telemetría mínima por source;
- almacenamiento opcional de metadata de eventos, no audio continuo;
- evaluación reproducible offline + E2E.

## OUT

- visión artificial;
- identificación de personas;
- análisis de conversaciones;
- inferencia de delitos;
- alta disponibilidad distribuida;
- auto-scaling cloud;
- fleet management de cientos de cámaras;
- entrenamiento de foundation model;
- garantía de distancia no validada.

## Demo mínima

`camera/replay -> audio -> inference -> confirmed event -> MQTT subscriber`, mostrando `source_id`, clase, confidence, tiempos y model/event-engine versions.