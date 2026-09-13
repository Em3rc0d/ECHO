# Product Hypotheses — MK1

MK1 convierte evidencia de MK0 en una primera vertical construible.

| ID | Hipótesis de producto | Criterio de validación | Estado |
|---|---|---|---|
| PH-01 | Una fuente RTSP/replay puede atravesar todo el pipeline sin acoplar el core al fabricante | E2E test con `source_id` y adapter reemplazable | CANDIDATE |
| PH-02 | Un backbone preentrenado + head ECHO ofrece mejor costo/beneficio inicial que entrenar desde cero | benchmark A/B/C | OPEN |
| PH-03 | Event Engine reduce duplicados y false alarms respecto a publicar cada ventana | replay temporal etiquetado | OPEN |
| PH-04 | MQTT QoS 1 + `event_id` permite consumidores idempotentes en PoC | duplicate/reconnect tests | CANDIDATE |
| PH-05 | La arquitectura soporta N sources aunque sólo una cámara real esté disponible | N replays concurrentes | CANDIDATE |

## Regla

Nada de esta lista autoriza `build`. Primero deben congelarse taxonomía, data manifests, benchmark, contracts y test plan.