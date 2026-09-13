# MK2 Capacity Plan

## Métricas por escala

Para cada N sources registrar:

```text
CPU total/per worker
RAM
windows/s
inference latency p50/p95/p99
queue depth/lag
dropped windows
source reconnects
broker publish latency
e2e event latency
```

## Workload profiles

### Quiet
Mayoría background/silence.

### Normal
Tráfico/eventos esporádicos.

### Burst
Múltiples fuentes generan eventos simultáneos.

### Degraded network
Jitter/disconnect/reconnect.

### Slow model
Artificially constrained inference para forzar backpressure.

## Resultado

Generar capacity envelope:

```text
hardware profile -> max certified sources under SLO
```

No usar specs teóricas del modelo como sustituto de este test.