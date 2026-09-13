# Hypotheses Register — MK0

| ID | Hipótesis | Cómo podría falsarse | Evidencia requerida | Estado |
|---|---|---|---|---|
| H-001 | YAMNet es baseline suficiente para PoC | PANNs/custom CNN lo supera claramente en calidad/latencia | benchmark común | OPEN |
| H-002 | 16 kHz mono preserva suficiente información para clases iniciales | caída material frente a 32/44.1 kHz | ablation por sample rate | OPEN |
| H-003 | Ventanas solapadas permiten alerta casi en tiempo real | p95 de latencia excede SLO o duplica eventos | replay + cámara | OPEN |
| H-004 | MQTT QoS 1 es suficiente para MK1 | pérdidas/duplicados no controlables con idempotencia | fault tests | OPEN |
| H-005 | Una taxonomía compacta mejora robustez | macro-F1/false alarms no mejora frente a taxonomía amplia | benchmark | OPEN |
| H-006 | FSD50K + datasets de benchmark aportan positivos útiles | domain mismatch severo con cámara | field validation | OPEN |
| H-007 | `OTHER/BACKGROUND` reduce falsas alarmas | no cambia o empeora calibración | hard-negative benchmark | OPEN |
| H-008 | Un único worker CPU puede servir la PoC | real-time factor > 1 o backlog creciente | profiling | OPEN |
| H-009 | Distancia nominal ~15 m es plausible para eventos intensos | recall cae bajo criterio definido | prueba 5/10/15/20/25 m | EXTERNAL_GATE_OPEN |
| H-010 | Audio de cámara estará disponible vía RTSP/NVR | cámara no expone micrófono/audio | ficha técnica + acceso real | EXTERNAL_GATE_OPEN |

## Regla

Una hipótesis nunca se promueve a `DECISION` por intuición. Debe enlazar dataset, experimento, métricas, hardware y evidencia reproducible.