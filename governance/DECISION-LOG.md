# Decision Log

Estados: `OPEN`, `CANDIDATE`, `CLOSED`, `EXTERNAL_GATE_OPEN`, `INVALIDATED`.

| ID | Decisión | Estado | Evidencia / razón |
|---|---|---|---|
| D-001 | Promesa oficial de ECHO | CLOSED | Project Charter; decisión del producto |
| D-002 | ECHO clasifica eventos observables, no delitos/situaciones | CLOSED | Límite semántico y verificabilidad |
| D-003 | Arquitectura multi-source desde MK1 | CLOSED | Evita rediseño por fuente física |
| D-004 | PoC puede validar 1 source real | CLOSED | Reduce costo sin cambiar contratos |
| D-005 | RTSP como ingestión primaria | CANDIDATE | Estándar ampliamente disponible en cámaras IP; validar cámara real |
| D-006 | ONVIF opcional, no hard dependency | CLOSED | RTSP explícito debe seguir siendo aceptado |
| D-007 | FFmpeg baseline de extracción/normalización | CANDIDATE | Ecosistema maduro; validar codecs reales |
| D-008 | go2rtc como relay opcional | CANDIDATE | Útil para fan-out/reconexiones; no necesario para 1 fuente |
| D-009 | MQTT/Mosquitto como event bus MK1 | CANDIDATE | Pub/Sub ligero, QoS, self-hosted |
| D-010 | YAMNet + ECHO head como baseline A | CLOSED para benchmark | Baseline compacto con transfer learning oficial |
| D-011 | PANNs/CNN14 como challenger B | CLOSED para benchmark | Alternativa fuerte preentrenada en AudioSet |
| D-012 | CNN propia log-mel como control C | CLOSED para benchmark | Control científico sin backbone preentrenado |
| D-013 | AST/HTS-AT/BEATs/PaSST en extended benchmark | OPEN | Evaluar footprint, latencia y licensing antes de MK2 |
| D-014 | Multi-label outputs con sigmoid | CANDIDATE | Eventos concurrentes son plausibles; confirmar taxonomía/data |
| D-015 | No usar gran clase OTHER monolítica | CANDIDATE | Preferir background/no-target + hard negatives + unknown |
| D-016 | Event Engine temporal con hysteresis/debounce/dedup | CLOSED conceptualmente | Evita convertir cada ventana en alerta |
| D-017 | Thresholds por clase desde validation set | CLOSED | Prohibido fijarlos por intuición |
| D-018 | Audio continuo no se retiene por defecto | CLOSED | Minimización y privacidad |
| D-019 | Attestation DAG en lugar de blockchain | CLOSED | Integridad/reproducibilidad sin consenso distribuido |
| D-020 | Licencia del código ECHO | OPEN | Apache-2.0 es candidata; requiere decisión del propietario |
| D-021 | Cámara/protocolo/codecs exactos | EXTERNAL_GATE_OPEN | Requiere acceso del docente/hardware |
| D-022 | Clases MK1 finales | OPEN | Deben resultar de mapping + data availability + field relevance |
| D-023 | Distancia nominal garantizada | OPEN | Requiere test 5/10/15/20/25 m |
| D-024 | SLOs finales | OPEN | Se congelan después de benchmark y PoC |

Una decisión `CLOSED` puede volver a `INVALIDATED` si cambia una dependencia upstream.