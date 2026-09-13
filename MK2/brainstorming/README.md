# MK2 / Brainstorming

## Pregunta

¿Qué debe ser cierto para que ECHO deje de ser una PoC convincente y sea un sistema operacionalmente confiable?

## Problemas que MK2 debe resolver

```text
N sources concurrentes
reconnect storms
slow/failed source isolation
bounded memory
fair scheduling
model rollout/rollback
schema evolution
message duplication
broker outage
storage outage
observability
configuration drift
field/domain drift
reproducible release
privacy enforcement
```

## Principio

MK2 no debe ocultar ML uncertainty detrás de infraestructura robusta. La resiliencia del sistema y la calidad del modelo se certifican por separado y luego como pipeline completo.

## Anti-features

No convertir MK2 en:

- NVR completo;
- plataforma de video analytics;
- SIEM;
- dispatch platform;
- reconocimiento de voz/personas;
- blockchain.

Cualquier integración externa consume eventos de ECHO; no redefine su core.