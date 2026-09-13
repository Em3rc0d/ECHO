# Multi-Source Boundary — MK1

Aunque exista una sola cámara física, el runtime debe aceptar una colección de `SourceDescriptor`.

```text
CAM-01 --┐
FILE-02 -┼-> source tasks -> independent buffers -> shared inference scheduler
FILE-03 -┘                                      -> event state keyed by source
```

## Validación sin N cámaras

Usar múltiples replays concurrentes con diferentes `source_id` y ritmos. Verificar aislamiento, fairness, memoria y que los eventos nunca mezclen identidades.

## No objetivo MK1

No fijar capacidad máxima de sources. El objetivo es demostrar que la arquitectura no está hardcodeada a uno; capacidad certificada pertenece a MK2.