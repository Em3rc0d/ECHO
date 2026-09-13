# Load & Soak Tests — MK2

## Load sweep

Incrementar N sources hasta detectar saturación. Medir CPU/GPU/RAM, queue depth, windows dropped, RTF y p95/p99 latency.

## Soak

Ejecutar carga representativa por horas suficientes para detectar memory leaks, file descriptor leaks, reconnect storms, clock drift y acumulación de queues.

## Pass

No existe pass universal: los límites se derivan de SLO Catalog. La prueba produce curva de capacidad y punto de degradación.