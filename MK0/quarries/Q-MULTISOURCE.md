# Quarry — Multi-Source

## Preguntas

- ¿1 proceso por source, tasks async o pool de workers?
- ¿Qué buffer máximo evita memoria ilimitada?
- ¿Qué hacer cuando inferencia no alcanza real time?
- ¿drop oldest, sample, backpressure o degrade gracefully?
- ¿cómo se conserva fairness entre fuentes?
- ¿cómo se identifica salud por source?

## PoC

Una cámara real puede validar conectividad; N replays concurrentes deben validar la abstracción multi-source.

## MK2

El número de fuentes soportadas no se promete hasta ejecutar capacity/load/soak tests en hardware objetivo.