# Definition of Ready — MK1 Build

**Status:** `CERTIFIED_FOR_REPLAY_BUILD`  
**Certificate:** `CERT-MK1-READY-001`

## 1. Qué certifica

La DoR certifica que el primer build puede comenzar sin improvisar decisiones que alteren el core. No afirma que el producto funcione ni que el modelo cumpla métricas; esas son salidas de build/test.

## 2. Dependencias upstream

- `CERT-MK0-013` válido.
- Promesa y anti-scope congelados.
- Taxonomía MK1 v1 congelada.
- Dataset policy y group-aware split definidos.
- Benchmark A/B/C definido.
- Source/audio/event contracts versionados.
- Event Engine lifecycle definido.
- Pub/Sub contract y delivery semantics definidos.
- Privacy/security baseline definida.
- Test plan preparado antes de implementación.

## 3. Checklist certificado

```text
[x] promise/scope
[x] semantic event boundary
[x] target taxonomy
[x] background/hard-negative policy
[x] asset provenance/license policy
[x] group-aware split policy
[x] field holdout plan
[x] benchmark A/B/C
[x] source abstraction
[x] audio normalization contract
[x] multi-source identity propagation
[x] raw inference schema
[x] candidate/confirmed lifecycle
[x] MQTT topics/payload semantics
[x] QoS1 + event_id idempotency
[x] secrets policy
[x] observability minimum
[x] error/failure strategy
[x] acceptance/test strategy
[x] replay path independent of real camera
```

## 4. Real-camera boundary

`EXT-CAMERA-001 = EXTERNAL_GATE_OPEN`. Esto no bloquea el vertical offline/replay porque source abstraction y file/replay adapter permiten validar el core. Sí bloquea afirmar:

```text
real camera supported
specific codec supported in field
measured RTSP reconnect behavior
measured field latency
measured distance/SNR performance
```

## 5. OPEN que no invalida Ready

Modelo ganador y thresholds son resultados del benchmark/validation. SLO final requiere medición. La licencia del código propio bloquea release, no desarrollo interno. Ninguno exige rediseñar el core antes de experimentar.

## 6. Regla de entrada a código

La primera implementación debe obedecer los contratos; no puede introducir singletons single-camera, thresholds mágicos ni publicación directa desde la red neuronal.

## 7. Evidencia requerida al salir de build

- commit reproducible;
- environment/dependency lock;
- dataset manifest hash;
- model/checkpoint hashes;
- configs;
- unit/integration/E2E results;
- metrics/error analysis;
- event logs de replay;
- known limitations.

## 8. Invalidation

La DoR se invalida si cambia promesa, taxonomía, contract schemas, source abstraction, benchmark comparability, Pub/Sub semantics o privacy policy de manera material.