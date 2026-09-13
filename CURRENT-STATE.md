# Estado actual de ECHO

**Fecha de corte:** 2026-09-13  
**Documento:** estado operativo y de certificación  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

Esta promesa es inmutable dentro del proyecto. Toda arquitectura, contrato, integración o funcionalidad se evalúa en función de si contribuye a detectar o clasificar eventos acústicos mediante IA. Cámaras, RTSP, ONVIF, brokers, dashboards, bases de datos y alertas son infraestructura de soporte.

## 2. Estado por milestone

```text
MK0
  brainstorming  = CERTIFIED
  design         = CERTIFIED
  arch           = CERTIFIED
  plan           = CERTIFIED
  build          = research-artifacts only
  test           = CERTIFIED
  milestone      = CERTIFIED

MK1
  brainstorming  = CLOSED_FOR_BUILD
  design         = CLOSED_FOR_BUILD
  arch           = CLOSED_FOR_BUILD
  plan           = CLOSED_FOR_BUILD
  build          = IN_PROGRESS
    data_foundry_spec        = CERTIFIED
    data_foundry_toolchain   = CERTIFIED
    data_corpus_execution    = OPEN_EXTERNAL_MEDIA_EXECUTION
    replay_audio_vertical    = BLOCKED_BY_CERTIFIED_CORPUS
  test           = DATA_FOUNDRY_TOOLCHAIN_PASS / FULL_MK1_PENDING
  milestone      = NOT_CERTIFIED

MK2
  brainstorming  = SPECIFIED
  design         = SPECIFIED
  arch           = SPECIFIED
  plan           = SPECIFIED
  build          = GATED
  test           = GATED
  milestone      = GATED_BY_MK1
```

## 3. Data Foundry — ingeniería cerrada hasta ejecución con media real

La transición `READY_NOT_STARTED -> IN_PROGRESS` ya ocurrió. El Data Foundry constituye el primer build real de MK1 y ahora tiene dos certificados distintos:

- `CERT-MK1-DF-SPEC-001 = CERTIFIED`: arquitectura, contratos, políticas y foundation.
- `CERT-MK1-DF-TOOLCHAIN-001 = CERTIFIED`: cadena ejecutable completa desde adquisición hasta handoff de benchmark.

### Cadena implementada

```text
source/acquisition registry
        ↓
publisher checksum verification
        ↓
source-specific metadata intake
        ↓
RawAssetCandidate JSONL
        ↓
technical audio probe + SHA-256
        ↓
license/use admission
        ↓
semantic mapping + manual review
        ↓
quality/quarantine
        ↓
group + exact/perceptual duplicate + label-conflict audit
        ↓
protected split / field holdout
        ↓
frozen asset/split/report bundle
        ↓
dataset manifest identities
        ↓
validated benchmark-facing split reader
```

### Toolchain verification

Certified engineering baseline: `2c4d4c2aae3e13de84680f65a79d5bb69301e18c`.

GitHub Actions run `34742947903` completed `success` on:

```text
Python 3.10 ✅
Python 3.11 ✅
Python 3.12 ✅
```

The Python 3.11 job ran **42 tests** and ended `OK`. Coverage includes acquisition, source adapters, rights admission, semantic mapping/review, technical audio probe, SHA-256/manifests, exact/perceptual duplicate guards, exact-byte label conflicts, deterministic splits, corrupt-audio quarantine and synthetic admission→freeze→benchmark-handoff E2E.

Two earlier CI runs failed because synthetic fixtures correctly triggered the near-duplicate guard. The gate was not disabled; test evidence was corrected and the complete matrix was rerun successfully. This is an intentional stop-the-line success, not hidden history.

## 4. What remains for the Data Foundry

There is **no remaining hidden Foundry implementation point** in DF-G0..DF-G8. The remaining node is execution against actual external source media:

```text
EXEC-DATA-001
  controlled storage + selected profile
        ↓
acquire/verify real releases
        ↓
run intake/admission/review/probe/dedup/split/freeze
        ↓
EMP-DATASET-001
        ↓
EMP-DATA-QUALITY-001
        ↓
CERT-MK1-DF-CORPUS-001
```

This is intentionally not marked complete without the real dataset bytes. Certifying exact counts, durations, diversity, duplicates or coverage before acquisition would be fabricated evidence.

### Known sourcing gaps carried forward

`FIRE_ALARM` and `TIRE_SQUEAL` still require defensible direct real assets for a release-safe corpus if the real Foundry execution confirms the current research landscape. Generic `Alarm`, `Screech`, `Friction brake` or similarly broad labels will not be coerced into those targets.

## 5. Foundry outputs and benchmark boundary

A real freeze must produce:

```text
asset-manifest.jsonl
split-manifest.json
dataset-manifest.json
coverage-report.json
dedup-report.json
quarantine-report.json
```

Benchmark code must validate the frozen bundle and enumerate train/validation/test only from its manifest. Arbitrary directory scanning or manual post-freeze file selection is non-certifiable.

## 6. Estado documental

The latest toolchain documentation expansion triggered a new audit by policy. Documentation certificate lineage is now:

```text
CERT-DOC-001  historical / INVALIDATED for later corpus
CERT-DOC-002  historical / INVALIDATED-SUPERSEDED
CERT-DOC-003  current / CERTIFIED
Markdown corpus under CERT-DOC-003 = 197 files
```

Root, Governance, Research, MK0, MK1 and MK2 remain depth-pass `PASS`. The current audit is `governance/DOCUMENTATION-AUDIT-2026-09-13-MK1-FOUNDRY-TOOLCHAIN.md`.

## 7. Decisiones congeladas para MK1

`DECISION` ECHO nace lógicamente multi-source aunque la primera validación física pueda usar una sola cámara. Todas las unidades de audio, inferencia, estado y eventos llevan `source_id`.

`DECISION` La ruta primaria de cámara es RTSP; ONVIF se usa como discovery/config cuando esté disponible, sin convertirlo en dependencia obligatoria.

`DECISION` FFmpeg es el decoder/extractor baseline y GStreamer queda como alternativa cuando jitter/reconexión/transport requieran mayor control.

`DECISION` El benchmark mínimo compara A = YAMNet + ECHO head, B = PANNs/Cnn14 + ECHO head y C = CNN compacta log-mel propia.

`DECISION` La taxonomía MK1 v1 usa `GLASS_SHATTER`, `SIREN`, `FIRE_ALARM`, `VEHICLE_HORN`, `TIRE_SQUEAL`; `BACKGROUND_NO_TARGET` es estado de datos y `UNKNOWN` es abstención del decision layer.

`DECISION` La salida target es multi-label; un mismo intervalo puede contener más de un evento.

`DECISION` El lifecycle es `RAW_INFERENCE -> CANDIDATE_EVENT -> CONFIRMED_EVENT -> ALERT/PUBSUB` y las ventanas de inferencia nunca se publican directamente como alarmas.

`DECISION` MQTT/Mosquitto es el bus inicial; confirmed events/alerts usan QoS 1 con `event_id` idempotente porque QoS 1 permite duplicados.

`DECISION` No se retiene audio continuo por defecto, no se incorpora ASR continuo ni identificación de hablantes.

`DECISION` El corpus del benchmark se selecciona únicamente mediante manifests Foundry versionados y validados; no existe selección manual silenciosa de archivos.

## 8. Nodos abiertos por evidencia empírica

`EMP-DATASET-001` Corpus real admitido: counts/durations/groups/license distribution y manifest identity producidos por `EXEC-DATA-001`.

`EMP-DATA-QUALITY-001` Calidad/duplicates/diversidad del corpus real: hashes, probes, dedup y source-diversity evidence.

`CERT-MK1-DF-CORPUS-001` Foundry corpus certificate: requires DF-G0..DF-G8 PASS against a named real profile/manifest.

`EMP-MODEL-001` Modelo ganador: requiere ejecutar benchmark A/B/C sobre el corpus certificado.

`EMP-THRESH-001` Thresholds: derivados del validation set y streaming replay por clase.

`EMP-DIST-001` Distancia/SNR: necesita ensayos reales autorizados por distancia, ruido, codec, orientación y dispositivo.

`EMP-CAP-001` Capacidad multi-source: requiere load/soak sobre hardware objetivo; no se promete N antes de medir.

`EMP-SLO-001` SLOs finales: se congelan después de evidencia MK1.

## 9. Gates externos

`EXT-CAMERA-001 = EXTERNAL_GATE_OPEN`. Falta marca/modelo, confirmación de audio, perfil RTSP, posible ONVIF, codec/sample-rate, red, credenciales autorizadas, permisos de prueba y condiciones de captura. No bloquea `EXEC-DATA-001` ni replay, pero bloquea claims de campo.

La ejecución de datasets públicos no depende de la cámara, pero sí necesita almacenamiento controlado y adquisición real de los bundles declarados; esta dependencia operacional está registrada como ejecución, no como un supuesto resuelto.

## 10. Siguiente transición autorizada

```text
CERT-MK1-DF-SPEC-001       ✅
CERT-MK1-DF-TOOLCHAIN-001  ✅
        ↓
EXEC-DATA-001              ← NEXT
        ↓
EMP-DATASET-001
EMP-DATA-QUALITY-001
        ↓
CERT-MK1-DF-CORPUS-001
        ↓
ReplaySource + canonical audio pipeline
        ↓
A/B/C benchmark
        ↓
EMP-MODEL-001 + EMP-THRESH-001
```

## 11. Invalidation

Si cambia la promesa, taxonomía, source/audio/event contract, benchmark set, Foundry source/acquisition registry semantics, mapping/admission/review/probe/dedup/split/manifest/handoff semantics, delivery semantics, privacy policy or audited Markdown corpus, revisar `governance/CERTIFICATION-DAG.md` y marcar los dependientes como `INVALIDATED` hasta revalidación.
