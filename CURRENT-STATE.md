# Estado actual de ECHO

**Fecha base:** 2026-09-13

## Resumen

El repositorio se inicializó desde cero. La investigación profunda ya produjo suficiente evidencia para formalizar MK0 y diseñar MK1/MK2, pero **no existe todavía implementación de producto**. Esto es intencional.

## Cerrado

- Promesa inmutable de producto.
- Estructura evolutiva MK0 / MK1 / MK2.
- Orden interno `brainstorming -> design -> arch -> plan -> build -> test`.
- Arquitectura multi-source desde origen; PoC físicamente unipunto permitida.
- Separación `RAW_INFERENCE -> CANDIDATE_EVENT -> CONFIRMED_EVENT -> ALERT/PUBSUB`.
- RTSP como camino primario de ingestión; ONVIF como discovery/config opcional.
- FFmpeg como baseline de decodificación/extracción; go2rtc queda opcional.
- MQTT/Mosquitto como candidato principal de Pub/Sub para MK1.
- YAMNet como baseline candidato, no ganador definitivo.
- Benchmark obligatorio contra challengers.
- Privacidad: sin ASR/speaker ID y sin retención continua por defecto.
- Certificación mediante DAG de evidencia/attestations, no blockchain.

## Abierto

- Modelo exacto ganador después del benchmark.
- Taxonomía MK1 final y mapping de labels.
- Thresholds por clase.
- Métrica/target de distancia real.
- Hardware mínimo certificado.
- Cámara real: marca/modelo/audio/codecs/protocolo/red/credenciales.
- Dataset de campo y estrategia de captura real.
- SLOs finales de MK2 después de MK1.

## Estado de build

```text
MK0/build  = GATED / NOT_STARTED
MK1/build  = GATED / NOT_STARTED
MK2/build  = GATED / NOT_STARTED
```

El siguiente trabajo es cerrar MK0 y los external gates; luego se certifica la Definition of Ready de MK1.