# Scaling Hypotheses — MK2

| ID | Hipótesis | Prueba |
|---|---|---|
| SH-01 | separar ingestion e inference mejora aislamiento | fault/load comparison |
| SH-02 | batching entre sources aumenta throughput sin romper latency SLO | batch-size/latency sweep |
| SH-03 | queues acotadas evitan colapso ante overload | overload soak |
| SH-04 | edge processing reduce red/privacidad | edge vs central profile |
| SH-05 | QoS1 + durable event store es suficiente para alerting normal | broker restart/replay tests |
| SH-06 | model drift puede detectarse con score/data telemetry | field drift analysis |

Todas permanecen abiertas hasta benchmark MK2.