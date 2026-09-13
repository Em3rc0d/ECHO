# Certification Ledger

El ledger registra qué evidencia/decisión ha sido certificada y de qué depende. El Git commit que contiene este documento funciona como envelope inmutable de esa versión del ledger.

## Estados

`OPEN` · `CANDIDATE` · `CERTIFIED` · `INVALIDATED` · `EXTERNAL_GATE_OPEN`

## MK0 certificates

| Certificate ID | Artefacto/claim | Estado | Inputs principales | Invalida si cambia |
|---|---|---|---|---|
| CERT-ECHO-000 | Promesa inmutable | CERTIFIED | PROJECT-CHARTER | promesa del propietario |
| CERT-MK0-001 | Boundary: eventos acústicos observables | CERTIFIED | charter + anti-scope | promise/boundary |
| CERT-MK0-002 | Landscape de modelos | CERTIFIED | TensorFlow, PANNs, AST, HTS-AT, PaSST, BEATs | source/version material |
| CERT-MK0-003 | Landscape de datasets | CERTIFIED | AudioSet, FSD50K, SONYC, ESC-50, DCASE | license/release facts |
| CERT-MK0-004 | RTSP source abstraction | CERTIFIED | ONVIF + FFmpeg/GStreamer docs | source contract |
| CERT-MK0-005 | FFmpeg baseline MK1 | CERTIFIED | FFmpeg docs + codec abstraction | incompatible required codec |
| CERT-MK0-006 | Multi-label inference contract | CERTIFIED | YAMNet + SONYC + polyphonic SED | taxonomy semantics |
| CERT-MK0-007 | Event lifecycle separation | CERTIFIED | SED/event-system design | event contract |
| CERT-MK0-008 | MQTT/Mosquitto MK1 bus | CERTIFIED | OASIS MQTT + Mosquitto + Frigate precedent | delivery requirements |
| CERT-MK0-009 | QoS1 + idempotency | CERTIFIED | MQTT 5.0 semantics | delivery semantics |
| CERT-MK0-010 | MK1 target taxonomy v1 | CERTIFIED | AudioSet evidence + domain relevance | label/data evidence |
| CERT-MK0-011 | Benchmark protocol v1 | CERTIFIED | model/data/metrics research | target taxonomy/model set |
| CERT-MK0-012 | Privacy-by-design requirement | CERTIFIED | project policy + Peru normative evidence | jurisdiction/policy |
| CERT-MK0-013 | MK0 research gate | CERTIFIED | CERT-MK0-001..012 | any dependency above |
| CERT-MK1-READY-001 | MK1 replay-build readiness | CERTIFIED | MK0 + DoR | any architecture-changing dependency |
| EXT-CAMERA-001 | Real camera integration | EXTERNAL_GATE_OPEN | brand/model/audio/RTSP/codec/network/access | closes only with field evidence |
| EMP-MODEL-001 | Model winner | OPEN | MK1 benchmark results | n/a |
| EMP-DIST-001 | Distance/SNR envelope | OPEN | field tests | n/a |
| EMP-SLO-001 | Final SLOs | OPEN | MK1 runtime/quality evidence | n/a |

## Dependency DAG

```text
CERT-ECHO-000
  -> CERT-MK0-001
      -> CERT-MK0-003 -> CERT-MK0-010
      -> CERT-MK0-002 -> CERT-MK0-011
      -> CERT-MK0-004 -> CERT-MK0-005
      -> CERT-MK0-006 -> CERT-MK0-007 -> CERT-MK0-008 -> CERT-MK0-009
      -> CERT-MK0-012

CERT-MK0-002..012
  -> CERT-MK0-013
  -> CERT-MK1-READY-001

CERT-MK1-READY-001 -> MK1/build -> MK1/test
EXT-CAMERA-001 -----> real-camera test branch
MK1/test -----------> EMP-MODEL-001 / EMP-DIST-001 / EMP-SLO-001
```

## Invalidation

Un cambio de taxonomy, schema, source contract, model benchmark set, delivery semantics o privacy policy obliga a recalcular el hash/versión del artefacto afectado y pasar sus dependientes a `INVALIDATED` hasta re-auditar.

No se usa blockchain: Git + hashes de assets + manifests + CI attestations dan la propiedad requerida sin consenso distribuido.