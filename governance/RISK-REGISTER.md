# Risk Register / FMEA

Escala cualitativa: Probabilidad `L/M/H`; Impacto `L/M/H/Critical`.

| ID | Failure mode | P | I | Efecto | Mitigación / evidencia requerida |
|---|---|---:|---:|---|---|
| R-01 | Micrófono de cámara pobre | H | H | bajo recall / ruido | benchmark de cámara vs mic externo |
| R-02 | Cámara no expone audio | M | H | no hay fuente | external mic asociado a source_id |
| R-03 | Codec/AGC comprime transitorios | M | H | glass/impact degradados | test por codec/dispositivo |
| R-04 | RTSP jitter/packet loss | M | H | gaps/latencia | reconnect, bounded buffers, telemetry |
| R-05 | Domain shift web -> ambiente real | H | Critical | métricas offline engañosas | field dataset + holdout por site/device/session |
| R-06 | Falsas alarmas por hard negatives | H | Critical | sistema inutilizable | hard-negative mining + event engine + per-class threshold |
| R-07 | Clase crítica no detectada | M | Critical | miss operativo | priorizar recall, distance/SNR tests, reject/unknown |
| R-08 | Leakage de dataset | M | Critical científico | benchmark inflado | group split por source/session/original event |
| R-09 | Labels ambiguos | H | H | techo de performance | annotation guide + adjudicación |
| R-10 | Eventos simultáneos | H | H | softmax incorrecto | multi-label benchmark |
| R-11 | Threshold fijo global | H | H | precision/recall desigual | threshold por clase |
| R-12 | Cola sin límite | M | Critical | memory blow-up/latency spiral | bounded queues + backpressure |
| R-13 | Reconexión masiva simultánea | M | H | thundering herd | exponential backoff + jitter |
| R-14 | Broker MQTT caído | M | H | alertas no entregadas | detector desacoplado, buffer/outbox policy MK2 |
| R-15 | QoS1 duplica mensajes | H | M | eventos repetidos | event_id idempotente |
| R-16 | Replay desde altavoz engaña detector | M | H | evento acústico no-originario | documentar límite; anti-spoofing es research separado |
| R-17 | Relojes desalineados | M | M | timestamps inconsistentes | UTC + NTP + stream_session_id |
| R-18 | Model drift | M | H | degradación futura | regression replay + field benchmark por release |
| R-19 | Dataset/licencia incompatible | M | H | bloqueo legal/distribución | license manifest por asset |
| R-20 | Credenciales en Git | M | Critical | exposición de cámara/red | secret refs + scanners + .env.example |
| R-21 | Retención de conversaciones | M | H | privacy risk | no ASR, no continuous retention |
| R-22 | Hardware insuficiente | M | M/H | lag | capacity benchmark 1/4/10/N sources |
| R-23 | Dependencia YAMNet/TensorFlow rompe compatibilidad | M | M | build no reproducible | pin/hash model/runtime |
| R-24 | Métrica accuracy oculta imbalance | H | H | decisión mala | macro/micro F1, PR-AUC, per-class recall |
| R-25 | Distancia prometida sin medir | H | H | requisito falso | 5/10/15/20/25 m protocol |

El register se revisa al final de cada `test/` y cualquier riesgo nuevo puede invalidar decisiones previas.