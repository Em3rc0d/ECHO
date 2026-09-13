# Definition of Done

**Status:** `NORMATIVE`

## 1. Principio

“Done” no significa que un script corre en una demo. Significa que el milestone cumple su scope certificado, genera evidencia reproducible y no deja deuda oculta que contradiga sus contratos. En ML, “100% funcional” tampoco significa 100% accuracy.

## 2. MK1 Definition of Done

MK1 debe demostrar una vertical completa:

```text
source/replay
  -> decode
  -> normalize
  -> window
  -> infer
  -> RAW_INFERENCE
  -> Event Engine
  -> CONFIRMED_EVENT
  -> MQTT
  -> subscriber/persistence/query
```

### Calidad ML

Debe existir benchmark comparable A/B/C con splits válidos, métricas por clase, macro/micro F1, PR-AUC cuando aplique, false alarms/source-hour, misses, calibration y error analysis. Los thresholds deben provenir de validation; el test permanece congelado.

### Runtime

Medir p50/p95/p99 de inferencia y latencia end-to-end en hardware documentado. Registrar CPU/GPU/RAM, throughput y dropped/stale windows. No aceptar buffers ilimitados.

### Multi-source contract

Aunque haya una sola cámara física, N replays concurrentes deben verificar aislamiento por `source_id`, fairness básica, zero state leakage y bounded queues.

### Delivery

QoS y topic contract deben probar duplicados/reconnect. Consumers deben usar `event_id` para idempotencia. Caída del broker no puede tumbar el detector silenciosamente.

### Seguridad/privacidad

No secrets en Git, credenciales inyectadas externamente, logs sin passwords, no ASR/speaker ID y no retención continua por defecto.

### Reproducibilidad

Cada resultado relevante referencia commit, config, dataset manifest, model/checkpoint hash y runtime environment.

## 3. MK2 Definition of Done

Además de MK1:

- capacidad multi-source certificada en hardware objetivo;
- load + soak + backpressure tests;
- failure/chaos tests y recovery budgets;
- model/config/schema versioning;
- rollback probado;
- observability operacional y alertas de salud;
- release artifact reproducible;
- provenance/attestation chain;
- field holdout evaluado con SLOs congelados;
- data/model drift workflow;
- security/privacy release gate;
- third-party/SBOM/license inventory cerrado;
- incident and migration procedures probados en staging.

## 4. Evidencia mínima de cada check

Un checkbox solo vale con URI/path de evidencia, fecha, versión y resultado. “Probado manualmente” sin registro no certifica release.

## 5. Failure policy

Si un requisito no se puede medir por un gate externo, queda `EXTERNAL_GATE_OPEN`; no se marca PASS. Si falla un SLO, se documenta FAIL y se corrige o se cambia el SLO mediante decisión explícita con nueva evidencia.

## 6. Invalidation

Cualquier cambio de modelo, schema, preprocessing, event logic, broker semantics, runtime crítico o deployment profile obliga a ejecutar la subset correspondiente de regression/certification tests.