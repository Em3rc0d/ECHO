# Definition of Ready — MK1 Build

**Estado:** `CERTIFIED_FOR_REPLAY_BUILD`  
**Certificate:** `CERT-MK1-READY-001`

MK1/build puede comenzar en modo dataset/replay porque:

- [x] MK0 está certificado.
- [x] Promesa y scope IN/OUT congelados.
- [x] Clases MK1 finales aprobadas.
- [x] Label mapping documentado.
- [x] Hard negatives definidos.
- [x] Dataset registry y license checks definidos.
- [x] Split policy group-aware congelada.
- [x] Benchmark A/B/C definido.
- [x] Source abstraction congelada.
- [x] Pipeline de audio definido.
- [x] `RAW_INFERENCE -> CANDIDATE_EVENT -> CONFIRMED_EVENT -> ALERT` definido.
- [x] Event schemas versionados.
- [x] MQTT/Mosquitto + QoS1 + idempotency congelados para MK1.
- [x] Secrets policy definida.
- [x] Observability mínima definida.
- [x] Test plan preparado antes de escribir producto.
- [x] Acceptance targets se expresan como `TARGET`, nunca como resultados inventados.
- [x] Existe camino replay/dataset que no depende de cámara real.
- [x] No queda decisión `OPEN` que obligue a rediseñar componentes core.

## External branch

`EXT-CAMERA-001 = EXTERNAL_GATE_OPEN`.

Esto **no bloquea** el primer vertical replay/offline; sí bloquea:

- certificación de ingestión de cámara real;
- codec compatibility real;
- reconnect/jitter sobre hardware real;
- distance/SNR claims;
- end-to-end field latency.

## OPEN que no bloquea build

- licencia jurídica del código ECHO: bloquea release/distribución definitiva, no la ingeniería interna;
- modelo ganador: es output del benchmark;
- thresholds: output de validation;
- SLO final: output de MK1 evidence.

`READY` significa autorización para empezar a construir, no que la build ya exista.