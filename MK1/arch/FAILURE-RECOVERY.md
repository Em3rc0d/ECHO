# Failure & Recovery — MK1

| Fallo | Detección | Respuesta MK1 |
|---|---|---|
| RTSP disconnect | read timeout/EOF | state RECONNECTING + backoff |
| no audio track | probe failure | FAILED, evidencia clara |
| decoder crash | process exit | restart controlado |
| corrupt frame | decode error | drop + metric |
| inference exception | adapter error | source degraded; no evento falso |
| backlog | buffer depth | bounded drop/degrade policy |
| MQTT unavailable | publish error | retry acotado; no bloquear audio indefinidamente |
| duplicate QoS1 | repeated `event_id` | subscriber idempotency test |

## Principio

La recuperación no puede fabricar continuidad temporal. Gaps deben quedar observables para que un evento no se confirme usando ventanas separadas por una desconexión larga.