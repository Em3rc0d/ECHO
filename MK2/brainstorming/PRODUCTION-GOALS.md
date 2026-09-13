# Production Goals — MK2

MK2 significa producto limpio y funcional dentro del alcance certificado; no significa ML perfecto.

## Objetivos

- múltiples fuentes reales concurrentes;
- degradación aislada por source;
- backpressure explícito;
- event delivery observable e idempotente;
- model/taxonomy/config versioning;
- reproducibilidad de builds y benchmarks;
- seguridad/privacidad operacional;
- load/soak/fault tests;
- release gate con evidencia.

## No promesas automáticas

No se fija cantidad de cámaras, distancia máxima, uptime, precision o latencia hasta obtener mediciones del hardware/deployment target.