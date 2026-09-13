# MK2 / Arch

## Target topology

```text
                    ┌──────────────────┐
CAM/MIC 1..N ──────>│ Source Registry  │
                    └────────┬─────────┘
                             v
                    ┌──────────────────┐
                    │ Ingest Workers   │
                    │ bounded/source   │
                    └────────┬─────────┘
                             v
                    ┌──────────────────┐
                    │ Fair Scheduler   │
                    └────────┬─────────┘
                             v
               ┌─────────────┼─────────────┐
               v             v             v
          Inference W1  Inference W2  Inference Wn
               └─────────────┼─────────────┘
                             v
                    ┌──────────────────┐
                    │ Event Engine     │
                    └───────┬───┬──────┘
                            │   │
                            │   └────> Event Store/API
                            v
                     Reliable Publisher
                            v
                        MQTT Bus
                            v
                   subscribers/alerts
```

## Bounded everything

No componente puede crecer sin límite:

```text
bounded ring buffer/source
bounded ingest queue
bounded inference queue
bounded publish queue/outbox
bounded evidence retention
```

Cuando hay sobrecarga, la política de drop/degradation debe ser explícita y observable.

## Isolation

Una cámara corrupta o lenta no consume indefinidamente workers. Scheduler debe mantener fairness y timeouts.

## Horizontal evolution

Interfaces deben permitir separar:

```text
ingest nodes
inference nodes
event/publisher service
storage/api
broker
```

sin cambiar schemas core.