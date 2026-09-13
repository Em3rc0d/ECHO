# Model Regression — MK2

Cada candidate se compara contra stable en:

- per-class precision/recall/F1;
- false alarms/hour en long negatives;
- domain slices;
- calibration;
- event onset/merge behavior;
- p95 latency y memory;
- artifact size;
- field replay corpus versionado.

Una mejora de promedio no compensa automáticamente una regresión grave en una clase crítica; exceptions requieren decisión explícita.