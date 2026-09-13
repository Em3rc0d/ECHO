# Decision Log

Estados: `OPEN`, `CANDIDATE`, `CLOSED`, `EXTERNAL_GATE_OPEN`, `INVALIDATED`.

| ID | Decisión | Estado | Evidencia / razón |
|---|---|---|---|
| D-001 | Promesa oficial de ECHO | CLOSED | Project Charter; decisión del producto |
| D-002 | ECHO clasifica eventos observables, no delitos/situaciones | CLOSED | Límite semántico y verificabilidad |
| D-003 | Arquitectura multi-source desde MK1 | CLOSED | Evita rediseño por fuente física |
| D-004 | PoC puede validar 1 source real | CLOSED | Reduce costo sin cambiar contratos |
| D-005 | RTSP como interfaz primaria de ingestión MK1 | CLOSED | ONVIF Profile T + FFmpeg/GStreamer; cámara concreta sigue external gate |
| D-006 | ONVIF opcional, no hard dependency | CLOSED | RTSP explícito debe ser soportado sin discovery obligatorio |
| D-007 | FFmpeg baseline de extracción/normalización MK1 | CLOSED | RTSP UDP/TCP + madurez operativa; GStreamer queda fallback/challenger |
| D-008 | go2rtc no es dependencia core MK1 | CLOSED | Relay opcional si fan-out/reconnect lo justifica; Frigate muestra ese patrón |
| D-009 | MQTT + Mosquitto como event bus MK1 | CLOSED | OASIS MQTT + broker open-source + precedente Frigate |
| D-010 | YAMNet + ECHO head como baseline A | CLOSED | TensorFlow transfer-learning oficial |
| D-011 | PANNs/Cnn14 como challenger B | CLOSED | AudioSet pretraining + tagging/SED ecosystem |
| D-012 | CNN propia log-mel como control C | CLOSED | Control científico sin backbone preentrenado |
| D-013 | AST/HTS-AT/PaSST/BEATs | CLOSED | Investigados y diferidos a MK2/extended benchmark salvo fallo del set A/B/C |
| D-014 | Output target multi-label con sigmoid | CLOSED | Eventos concurrentes + SONYC multilabel + SED polifónico |
| D-015 | No usar una clase OTHER monolítica | CLOSED | `BACKGROUND_NO_TARGET` + hard negatives + `UNKNOWN` en decision layer |
| D-016 | Event Engine temporal con hysteresis/debounce/dedup | CLOSED | Evita convertir cada ventana en alerta |
| D-017 | Thresholds por clase desde validation | CLOSED | Thresholds no se fijan por intuición |
| D-018 | Audio continuo no se retiene por defecto | CLOSED | Minimización y privacy-by-design |
| D-019 | Attestation DAG en lugar de blockchain | CLOSED | Git/hashes/manifests/CI satisfacen integridad sin consenso distribuido |
| D-020 | Licencia del código propio ECHO | OPEN | Requiere decisión jurídica explícita del propietario; no cambia arquitectura |
| D-021 | Cámara/protocolo/codecs exactos | EXTERNAL_GATE_OPEN | Requiere hardware/acceso del docente |
| D-022 | Clases MK1 finales | CLOSED | `GLASS_SHATTER`, `SIREN`, `FIRE_ALARM`, `VEHICLE_HORN`, `TIRE_SQUEAL` |
| D-023 | Distancia nominal garantizada | EXTERNAL_GATE_OPEN | Requiere field test por distancia/SNR/device |
| D-024 | SLOs finales | OPEN | Se congelan con evidencia de MK1 |
| D-025 | Benchmark A/B/C v1 | CLOSED | YAMNet / PANNs Cnn14 / custom log-mel CNN, mismo split/protocolo |
| D-026 | Redis Pub/Sub como bus de alarmas | CLOSED (REJECTED) | No cumple semántica de entrega requerida para consumidor desconectado |
| D-027 | MQTT QoS 1 para confirmed events/alerts | CLOSED | At-least-once implica duplicados; `event_id` + idempotencia obligatorios |
| D-028 | PSDS como métrica secundaria si hay strong temporal labels | CLOSED | DCASE/polyphonic SED; no sustituye métricas operativas de ECHO |
| D-029 | Vehicle collision como label MK1 | CLOSED (DEFERRED) | No confundir impacto genérico con accidente vehicular confirmado; requiere dataset específico |

Una decisión cerrada puede volver a `INVALIDATED` si cambia una dependencia upstream.

## Empirical outputs

Modelo ganador, thresholds numéricos, distance envelope y SLOs **no son decisiones abiertas de arquitectura**: son resultados que deben producir MK1/MK2 test. Se mantienen OPEN/EXTERNAL hasta que exista evidencia.