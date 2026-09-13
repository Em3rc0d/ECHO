# MK1 Requirements

## Functional Requirements

| ID | Requisito | Prioridad |
|---|---|---|
| FR-001 | Registrar múltiples `SourceDescriptor` aunque solo una fuente esté activa | MUST |
| FR-002 | Ingerir audio desde replay/local y al menos un adapter RTSP cuando el hardware esté disponible | MUST |
| FR-003 | Normalizar input al formato requerido por el modelo activo | MUST |
| FR-004 | Mantener buffers limitados e independientes por source | MUST |
| FR-005 | Generar `RawInference` versionada por ventana | MUST |
| FR-006 | Soportar scores multi-label en el contrato interno | MUST |
| FR-007 | Agregar inferencias temporales en `CandidateEvent` | MUST |
| FR-008 | Confirmar/cerrar/deduplicar eventos mediante Event Engine | MUST |
| FR-009 | Publicar `ConfirmedEvent` en Pub/Sub | MUST |
| FR-010 | Persistir metadata de eventos sin requerir audio raw | MUST |
| FR-011 | Consultar eventos por tiempo/source/type | SHOULD |
| FR-012 | Exponer health/source state/metrics | MUST |
| FR-013 | Reconectar fuentes caídas con backoff | MUST para RTSP |
| FR-014 | Identificar cada stream session | MUST |
| FR-015 | Versionar model/config/schema en cada evento | MUST |
| FR-016 | Permitir replay reproducible de audio de evaluación | MUST |
| FR-017 | Registrar model inference latency y event latency | MUST |
| FR-018 | Emitir alertas como downstream policy, no desde score crudo | MUST |

## Non-Functional Requirements

| ID | Requisito | Tipo |
|---|---|---|
| NFR-001 | No bloquear N sources por falla de una | resilience |
| NFR-002 | Sin colas ilimitadas | reliability |
| NFR-003 | Secrets fuera de Git/logs | security |
| NFR-004 | Audio continuo no retenido por defecto | privacy |
| NFR-005 | Contratos JSON versionados | maintainability |
| NFR-006 | Tests y benchmark reproducibles | scientific validity |
| NFR-007 | Métricas per-class además de agregadas | ML quality |
| NFR-008 | Todos los artifacts críticos con hash/version | provenance |
| NFR-009 | Configuración separada del código | operability |
| NFR-010 | CPU viability se mide, no se asume | performance |
| NFR-011 | Deployment PoC debe poder funcionar local/self-hosted | cost/privacy |
| NFR-012 | No asumir conectividad cloud | resilience/cost |

## Requisitos que aún NO son valores cerrados

- accuracy/F1 exacto;
- false alarms/hour máximo;
- p95 latency exacta;
- distancia máxima;
- número de sources por nodo;
- thresholds por clase.

Se etiquetan `TARGET_CANDIDATE` hasta benchmark.