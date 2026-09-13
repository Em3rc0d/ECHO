# Definition of Done

## MK1

MK1 está DONE solo si existe evidencia reproducible de una vertical completa:

```text
source -> decode -> normalize -> infer -> aggregate -> confirmed event -> Pub/Sub -> persist/query
```

Además:

- contratos validados;
- tests unit/integration/e2e definidos y ejecutados;
- benchmark de modelos ejecutado sobre splits válidos;
- thresholds derivados de validation, no inventados;
- métricas por clase + false alarms/hour + latency;
- reconexión de stream probada;
- QoS/idempotencia probada;
- error analysis documentado;
- model/data/config hashes registrados;
- no secrets ni raw datasets en Git;
- limitaciones y fallos conocidos documentados.

## MK2

MK2 está DONE cuando, además de MK1:

- multi-source real o capacity test equivalente certificado;
- bounded queues/backpressure probado;
- model/config/schema versioning y rollback;
- observabilidad operacional;
- load/soak/failure/chaos tests;
- release artifact reproducible;
- provenance/attestation chain válida;
- field holdout cumple SLOs congelados;
- privacy/retention policy verificada;
- todos los external gates de release cerrados.

“100% funcional” significa cumplir el scope y DoD, **no** obtener 100% de precisión ML.