# Claim Checklist — MK0

Antes de escribir afirmaciones como requisito cerrado:

- `accuracy >= X` -> requiere benchmark ECHO, no paper externo;
- `latency < X` -> requiere hardware + stream real/replay representativo;
- `detecta a X metros` -> requiere protocolo de distancia y micrófono concreto;
- `MQTT no pierde eventos` -> falso como afirmación absoluta; especificar QoS, sesión, persistencia e idempotencia;
- `dataset libre` -> verificar licencia de dataset **y** de cada asset cuando aplique;
- `modelo open source` -> verificar código y checkpoint por separado;
- `cámara soporta audio` -> verificar modelo/configuración real;
- `OTHER resuelve OOD` -> hipótesis, no garantía.

El objetivo es impedir que marketing o intuición se conviertan en especificación.