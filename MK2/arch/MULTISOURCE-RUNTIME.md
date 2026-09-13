# Multi-Source Runtime — MK2

```text
Source Registry
      |
      v
Ingestion Supervisors (per source)
      |
      v
Bounded Audio Queues
      |
      v
Inference Scheduler / Worker Pool
      |
      v
Per-source Event State
      |
      v
Confirmed Event Bus
      +--> durable metadata
      +--> MQTT / external adapters
```

## Scheduler goals

- fairness entre sources;
- prioridad explícita si existe;
- batching opcional;
- deadline/lag awareness;
- no starvation;
- metrics de queue depth y dropped windows.

## Isolation

Un decoder corrupto o source flapping no reinicia el modelo compartido ni bloquea otras fuentes.