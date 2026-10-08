# Estado actual de ECHO

**Fecha de corte:** 2026-10-08  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Execution invariant:** `DOCKER_ONLY_RUNTIME`  
**Active MVP profile:** `ECHO-MVP-001`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

La promesa permanece inmutable. Cámara/NVR, RTSP/ONVIF, MQTT, UI, almacenamiento y alertas son infraestructura de soporte y no redefinen el core acústico.

## 2. Dos workstreams que no deben confundirse

ECHO mantiene simultáneamente:

### A. Full release corpus

La taxonomía mayor conserva trabajo abierto para clases como `FIRE_ALARM` y `TIRE_SQUEAL`. Sus gaps históricos de cobertura/licencia/diversidad no se consideran resueltos por el MVP reducido.

### B. ECHO-MVP-001

Para obtener evidencia end-to-end sin falsear el gate del corpus mayor, se congeló un MVP de tres clases:

```text
GLASS_SHATTER
SIREN
VEHICLE_HORN
```

`FIRE_ALARM` y `TIRE_SQUEAL` no fueron relabelados como background; simplemente quedaron fuera del benchmark MVP-001.

## 3. Frozen MVP dataset identity

```text
benchmark manifest rows       1027
development assets upstream   1061
SONYC required                 599
direct non-SONYC media         428 / 428
split quarantine               0
```

Positive counts:

| split | GLASS_SHATTER | SIREN | VEHICLE_HORN |
|---|---:|---:|---:|
| train | 84 | 75 | 81 |
| validation | 14 | 70 | 60 |
| test | 17 | 76 | 149 |

The complete 1,027-asset media cache was rehydrated before the real A/B/C benchmark.

## 4. Empirical model benchmark

The three declared arms were executed:

| Benchmark | Test macro F1 | Precision | Recall | Macro FPR |
|---|---:|---:|---:|---:|
| YAMNET_EMBEDDINGS_HEAD | 0.6675689376 | 0.7250183747 | 0.6271202582 | 0.1088042898 |
| PANNS_CNN14_HEAD | 0.7660443723 | 0.9170177762 | 0.6868597669 | 0.0147220036 |
| COMPACT_LOGMEL_CNN | 0.6977375998 | 0.6717409690 | 0.7950370894 | 0.2655885904 |

Model selection used validation evidence only. The test split did not select the winner.

Current selected candidate:

```text
PANNS_CNN14_HEAD
status = PROVISIONAL_MVP_WINNER
```

PANNs per-class clip-level test F1:

```text
GLASS_SHATTER   0.9714285714
SIREN           0.78125
VEHICLE_HORN    0.5454545455
```

Known weakness: VEHICLE_HORN sensitivity remains materially weaker than the other two targets.

## 5. Runtime vertical

The first vertical is operational in Docker:

```text
audio/replay
→ FFmpeg decode
→ selected model
→ per-window scores
→ Temporal Event Engine
→ echo.event.v1
→ MQTT QoS 1
→ consumer
```

Docker-only MQTT gate evidence:

```text
sent messages                  46
received messages              46
sent logical event_ids         23
received logical event_ids     23
missing_event_ids              []
missing_messages               []
unexpected_messages            []
exact_qos_duplicate_deliveries []
status                          PASS
```

A logical event intentionally reuses its deterministic `event_id` for `CONFIRMED` and `CLOSED` lifecycle messages.

## 6. Controlled temporal calibration

Controlled validation temporal calibration has been executed using:

```text
window = 6 s
hop    = 1 s
selection partition = temporal_tune
evaluation partition = temporal_holdout
test split used = false
```

Aggregate temporal holdout:

```text
macro F1              0.7261904762
macro recall          0.5833333333
false alarms/hour     0.0
```

The zero false-alarm observation applies only to the limited controlled holdout and is **not** a field false-alarm claim.

Selected controlled policies:

| class | on | off | confirm | release | holdout recall | holdout F1 |
|---|---:|---:|---:|---:|---:|---:|
| GLASS_SHATTER | 0.35 | 0.15 | 3 | 1 | 0.75 | 0.8571 |
| SIREN | 0.60 | 0.40 | 1 | 1 | 0.60 | 0.75 |
| VEHICLE_HORN | 0.75 | 0.55 | 1 | 1 | 0.40 | 0.5714 |

Current boundary:

```text
ECHO-MVP-001-TEMPORAL-CONTROLLED-v1
CONTROLLED_VALIDATION_CALIBRATED_NOT_FIELD_CALIBRATED
```

This configuration is suitable for controlled demo/replay work, not for production or field-performance claims.

## 7. Professor demo

A Docker-only presentation surface exists on:

```text
http://localhost:8088
```

It uses the real selected scorer and Temporal Event Engine; detections are not hardcoded.

Included:

- four governed controlled-validation scenarios;
- blind WAV upload;
- ephemeral browser microphone capture;
- score diagnostics for external audio;
- `NO_TARGET` and conservative `UNKNOWN / ABSTAIN`;
- MQTT for governed accepted events.

The demo scope is frozen in:

```text
demo/DEMO-SCOPE-FREEZE.md
```

Reproducible operator steps are in:

```text
demo/docker-runbook/
```

## 8. False-positive evidence from external audio

Ad hoc target-free testing exposed failures outside controlled validation:

### Ambient-only

Approximately 51 s of ordinary ambient sound produced:

```text
GLASS_SHATTER ~55% peak
SIREN         ~70% peak
2 logical target events
```

This remains an unresolved environmental-domain false-positive signal.

### Voice-only

Approximately 4.1 s of normal voice produced:

```text
GLASS_SHATTER ~56% peak
1 logical event
5 analyzed windows
```

The five-window behavior exposed a real demo/replay artifact: external clips shorter than the 6 s analysis window were processed with repeated zero-padded tail windows.

Containment merged:

- external audio now uses `pad_final=False`;
- at least one complete analysis window is required;
- short microphone captures are rejected;
- per-class score traces are exposed;
- external candidates are subject to `ECHO-DEMO-ABSTENTION-v1`;
- uncalibrated external target candidates are not published as accepted MQTT target events.

The padding defect is contained. The broader model/domain-confuser problem remains open.

Canonical analysis:

```text
MK1/test/FALSE-POSITIVE-ANALYSIS-2026-10-08.md
```

Active robustness gate:

```text
MK1/test/FIELD-AUDIO-ROBUSTNESS-GATE.md
issue #53
```

## 9. Current decision-layer semantics for external demo audio

```text
external mic/WAV
      ↓
real 3-class scorer
      ↓
Temporal Event Engine
      ↓
no target candidate ──────→ NO_TARGET
target candidate(s) ──────→ UNKNOWN / ABSTAIN
                                  ↓
                         no accepted target MQTT event
```

This is a conservative demo boundary, not a learned/calibrated OOD detector.

A true OOD/target-rejection solution remains future MVP work.

## 10. MVP-002

The proposed future class expansion is:

```text
SCREAM
GUNSHOT
FIRE_ALARM
COLLISION_IMPACT
```

Status:

```text
DESIGN_ONLY / BUILD_BLOCKED
```

Current three classes + those four would produce a seven-target proposal, but no new target has been added to the active checkpoint.

MVP-002 remains blocked until the three-class environmental false-positive/robustness gate is understood and closed.

See issue #54 and:

```text
MK1/design/ECHO-MVP-002-CLASS-EXPANSION.md
```

## 11. Current critical path

```text
three-class controlled MVP vertical       PASS
Docker image/runtime                      PASS
real A/B/C benchmark                      PASS
PANNS_CNN14_HEAD provisional selection    PASS
real-audio replay/Event Engine smoke      PASS
MQTT QoS1 roundtrip                       PASS
controlled temporal calibration           EXECUTED
professor demo                            IMPLEMENTED / SCOPE FROZEN
short external padding defect             CONTAINED

environmental false-positive profile      OPEN
hard-negative mining iteration            OPEN
field/OOD acceptance policy               OPEN
operating-envelope freeze                 OPEN
real camera branch                        EXTERNAL / OPEN
MVP-002 build                              BLOCKED
MK2                                       GATED
```

## 12. Immediate engineering priority after the demo

Do not expand presentation scope.

The real MVP should now focus on:

```text
target-free environmental capture
→ score/candidate localization
→ confuser taxonomy
→ hard-negative mining
→ validation-side retraining/recalibration
→ frozen candidate
→ untouched environmental/field holdout
→ false alarms per source-hour
→ operating envelope
```

No arbitrary threshold should be tuned from one demo screenshot or one ad hoc recording.

## 13. Execution law

ECHO runtime/integration is Docker-only.

The host is limited to:

- Docker engine / Docker Desktop;
- source repository;
- artifact storage;
- browser/operator tooling.

Do not require host-installed Python, FFmpeg, Mosquitto, TensorFlow, PyTorch or PANNs for the MVP runtime.

## 14. Evidence boundary

A successful professor demo is useful engineering evidence, but it does not establish:

- zero false positives;
- field calibration;
- production readiness;
- camera distance/SNR envelope;
- a learned OOD detector;
- support for untrained classes.

The correct status is a functioning three-class Docker MVP vertical with controlled-validation evidence and an open environmental robustness gate.
