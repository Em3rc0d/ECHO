# MK2 SLO Framework

## Dimensiones

### ML quality

```text
critical recall
precision
macro F1
false alarms/source-hour
calibration
```

### Realtime

```text
onset -> confirmed_event p50/p95/p99
queue lag
publisher delay
```

### Reliability

```text
source recovery time
service availability during soak
message delivery success
idempotency correctness
```

### Capacity

```text
active sources/node
windows/s
CPU/RAM
backpressure events
```

## Candidate gates from research

Los valores investigados (por ejemplo macro F1 ~0.90, false alarms ~0.05/source-hour o p95 ~1.5–2 s) se consideran **objetivos exploratorios**, no SLOs oficiales.

El proceso correcto:

```text
MK1 evidence
  ↓
error/capacity analysis
  ↓
operational requirement
  ↓
SLO proposal
  ↓
approval
  ↓
MK2 test gate
```

## Error budget

Para componentes operacionales puede definirse error budget (stream outages, publish failures, source unavailable), pero no maquillar fallos de clasificación bajo un availability SLO.