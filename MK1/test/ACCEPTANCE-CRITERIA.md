# MK1 Acceptance Criteria

## No confundir targets con resultados

Los siguientes son **TARGET_CANDIDATE**, pendientes de congelar después del baseline inicial:

| Métrica | Target candidate | Estado |
|---|---:|---|
| Macro F1 offline | >= 0.85 | HYPOTHESIS/TARGET |
| Recall de clases críticas | >= 0.90 | HYPOTHESIS/TARGET |
| Precision de clases críticas | >= 0.85 | HYPOTHESIS/TARGET |
| E2E latency p95 | <= 2.0 s | HYPOTHESIS/TARGET |
| False alarms | <= 0.5/source-hour en test controlado | HYPOTHESIS/TARGET |
| RTSP reconnect | automático | REQUIREMENT |
| MQTT duplicate handling | idempotente | REQUIREMENT |
| Source isolation | una caída no bloquea otras | REQUIREMENT |
| Secrets in repo | 0 | REQUIREMENT |

Estos valores no deben publicarse como performance de ECHO hasta tener evidencia.

## Certificación

MK1 pasa solo si:

1. requisitos MUST están implementados/probados;
2. métricas se calculan sobre un test válido;
3. failures conocidos están documentados;
4. cualquier target incumplido genera decisión explícita de redesign, scope o SLO; nunca se oculta.