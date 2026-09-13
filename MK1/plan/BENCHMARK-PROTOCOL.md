# MK1 Benchmark Protocol v1

**Estado:** `FROZEN_FOR_EXECUTION`  
**Decision:** D-025  
**Certificate:** CERT-MK0-011

## Objetivo

Seleccionar el modelo operativo de ECHO por evidencia del dominio ECHO, no por leaderboard externo.

## Model set obligatorio

```text
A — YAMNet embeddings + ECHO multi-label head
B — PANNs Cnn14 (preferir 16 kHz checkpoint/recipe cuando sea técnicamente equivalente) + ECHO head
C — ECHO custom CNN sobre log-mel, sin pretrained backbone
```

AST/HTS-AT/PaSST/BEATs quedan como benchmark extendido/MK2 o fallback si A/B/C no satisface constraints.

## Data protocol

1. Cada asset debe tener provenance + license + hash.
2. Preservar split oficial cuando sea metodológicamente relevante.
3. Para datasets combinados, split **group-aware**: nunca separar fragmentos del mismo source/session/recording/event entre train/validation/test.
4. Mantener `field_holdout` separado y no tocarlo durante tuning.
5. Augmentation solo en train.
6. Hard negatives deben aparecer en validation/test sin leakage.
7. Si se usan múltiples seeds, el conjunto de seeds se fija en el run manifest antes de entrenar y no cambia por resultados.

No se impone 70/15/15 cuando el dataset ya ofrece folds/splits oficiales; el criterio de independencia es más importante que un porcentaje arbitrario.

## Fairness de benchmark

A/B/C comparten:

- taxonomía;
- exactamente los mismos groups/splits;
- augmentation policy;
- loss/imbalance policy documentada;
- early-stopping rule;
- threshold calibration policy;
- hardware y runtime budget;
- warm-up policy;
- batch/streaming policy;
- número de runs/seeds definido antes de mirar resultados.

## Metrics — calidad

Por clase:

```text
Precision
Recall
F1
PR-AUC / average precision
confusion/confuser analysis
```

Global:

```text
macro F1
micro F1
macro PR-AUC
```

Si existe strong temporal ground truth suficiente:

```text
PSDS / polyphonic SED score (secondary)
event-based onset/offset metrics
```

## Metrics — streaming

```text
false alarms / source-hour
misses / target class
detection latency p50/p95/p99
onset error
duration error
duplicate confirmed events / source-hour
```

## Metrics — runtime

```text
inference latency p50/p95/p99
CPU utilization
RAM peak/steady
model size
windows/second
real-time factor
queue depth / dropped windows under load
```

## Calibration

- threshold por clase se aprende **solo** en validation;
- test no participa en threshold tuning;
- reportar reliability curves/Brier/ECE cuando sean interpretables;
- registrar operating point exacto en model manifest.

## Selection rule

No existe score mágico. Selección Pareto:

```text
maximize critical-class recall and macro F1
while minimizing false alarms/source-hour
subject to latency/resource constraints measured on target-class hardware
```

Los constraints numéricos se marcan `TARGET_CANDIDATE` hasta que el hardware/uso real permita congelarlos.

## Output obligatorio

El benchmark produce un `MODEL-SELECTION-REPORT` con:

- config hashes;
- data manifest hash;
- model/checkpoint hashes;
- environment/hardware;
- raw metrics;
- error analysis;
- Pareto comparison;
- winner o `NO_MODEL_MEETS_CONSTRAINTS`.

Nunca se fuerza un ganador.