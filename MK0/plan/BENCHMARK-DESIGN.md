# Benchmark Design — MK0

## Objetivo

Seleccionar estrategia de modelo y parámetros de pipeline por evidencia propia.

## Comparación mínima

- A: YAMNet frozen embeddings + head ECHO.
- B: PANNs/CNN14 feature extraction/fine-tuning.
- C: custom compact log-mel CNN.

Transformers/self-supervised se añaden sólo si recursos y export permiten un experimento comparable.

## Controles

- mismo manifest de datos;
- splits group-aware para evitar leakage de source/uploader/recording;
- mismas clases y política de `OTHER`;
- mismo protocolo de ruido y domain holdout;
- reporte por clase y agregado;
- hardware fijado y calentamiento antes de latencia.

## Métricas

`precision`, `recall`, `F1`, `macro-F1`, PR-AUC cuando corresponda, `false_alarms/hour`, miss rate, ECE/Brier para calibración, p50/p95/p99 latency, real-time factor, CPU/GPU/RAM y tamaño del artefacto.

## No permitido

Elegir ganador por una métrica de paper no reproducida en el dominio de ECHO.