# Incident Plan — MK2

## Incidentes tipo

- múltiples sources down;
- broker unavailable;
- runaway false positives;
- model rollout regression;
- storage full;
- credential exposure;
- corrupted checkpoint/config;
- clock/timestamp anomaly.

## Respuesta

Detect -> contain -> preserve evidence -> rollback/degrade -> recover -> postmortem -> update risk/fixtures.

## Kill switches

Debe existir forma de deshabilitar source, clase/event policy o publisher sin borrar configuración ni redeploy completo cuando sea operativamente razonable.