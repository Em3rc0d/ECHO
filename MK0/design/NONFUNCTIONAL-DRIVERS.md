# Non-Functional Drivers — MK0

## Latencia

Medir end-to-end desde timestamp de captura hasta evento publicado. Reportar p50/p95/p99; no usar solo promedio. El SLO se congela después de benchmark de hardware/cámara.

## Calidad ML

Métricas mínimas: precision/recall/F1 por clase, macro-F1, matriz de confusión, false alarms/hour, miss rate, calibración y rendimiento por condición de ruido/distancia.

## Throughput

La unidad operativa es `source-stream`. Medir real-time factor por source, backlog, uso CPU/RAM/GPU y degradación cuando N aumenta.

## Resiliencia

El sistema debe definir reconexión, buffers acotados, backpressure, timeouts, manejo de codecs inválidos y aislamiento por source.

## Privacidad

Minimización de audio, retención desactivada por defecto, acceso a secretos fuera del repo y prohibición de reconocimiento de contenido conversacional.

## Reproducibilidad

Cada resultado debe enlazar versión de dataset manifest, split, modelo/checkpoint, preprocessing, configuración, seed cuando aplique y hardware.