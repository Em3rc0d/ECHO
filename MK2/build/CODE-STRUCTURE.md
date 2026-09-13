# Planned Code Evolution — MK2

Sobre la estructura MK1, MK2 probablemente introduce:

```text
src/echo/
├── scheduling/
│   ├── fairness.py
│   ├── batching.py
│   └── backpressure.py
├── registry/
│   ├── models.py
│   ├── configs.py
│   └── schemas.py
├── messaging/
│   ├── outbox.py
│   └── delivery.py
├── provenance/
│   ├── attest.py
│   ├── verify.py
│   └── release_manifest.py
├── operations/
│   ├── health.py
│   ├── rollback.py
│   └── migrations.py
└── observability/
    ├── metrics.py
    ├── tracing.py
    └── structured_logging.py

tests/
├── load/
├── soak/
├── resilience/
├── chaos/
├── compatibility/
└── release/
```

Es un plan de estructura, no código aprobado.