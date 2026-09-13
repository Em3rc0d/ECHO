# Reference Architectures — MK0

## A. Single-process PoC

```text
RTSP/file -> decoder -> window -> model -> event engine -> MQTT
```

Ventaja: mínima complejidad. Riesgo: acoplamiento y menor aislamiento.

## B. Multi-source modular target

```text
Sources -> Ingestion workers -> bounded queues -> Inference workers
                                  |                 |
                                  +-> metrics       v
                                              Event Engine
                                                   |
                                            Confirmed Events
                                           /       |       \
                                      MQTT      Store      API
```

## C. Edge-first

Cada sitio procesa localmente y publica sólo eventos/telemetría. Reduce ancho de banda y exposición de audio, pero complica distribución de modelos y observabilidad.

## D. Central inference

Streams llegan a un nodo central. Simplifica gestión de modelos, pero aumenta red, superficie de fallo y dependencia de conectividad.

## Decisión candidata

MK1 debería usar un proceso modular en una máquina y mantener boundaries compatibles con separación futura. MK2 decide edge/central/híbrido con evidencia de capacidad y red.