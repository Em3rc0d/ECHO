# Quarry — Latency

Descomponer:

`capture/buffer + decode/resample + window wait + inference + event confirmation + publish`.

Medir cada tramo y total. Un modelo rápido no garantiza alerta rápida si el Event Engine exige mucha evidencia. Reportar p50/p95/p99 y onset-to-confirmed-event delay.

No prometer `<2 s` hasta medir con hardware y cámara representativos.