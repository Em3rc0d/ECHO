# MK1 Benchmark Protocol

## Objetivo

Seleccionar baseline/model candidate por evidencia del dominio ECHO, no por leaderboard externo.

## Modelos mínimos

```text
A YAMNet + ECHO head
B PANNs/Cnn14 + ECHO head
C ECHO custom CNN log-mel
```

## Dataset split

Group-aware. Nunca separar clips del mismo evento/grabación física entre train y test.

Suggested structure, no dogma:

```text
train ~70%
validation ~15%
test ~15%
+
field_holdout = completely untouched
```

## Training fairness

- mismas clases;
- mismos groups/splits;
- augmentations solo train;
- early stopping definido;
- seed(s) registradas;
- class imbalance strategy registrada;
- calibración de threshold solo validation.

## Metrics

### Clip/window

```text
precision[class]
recall[class]
F1[class]
macro F1
micro F1
PR-AUC[class]
```

### Streaming replay

```text
false alarms / source-hour
misses / class
detection latency p50/p95/p99
onset error
duration error
```

### Runtime

```text
CPU%
RAM
model size
windows/s
inference p50/p95
```

### Calibration

```text
Brier score
reliability curve
ECE if appropriate
```

## Selection rule

No utilizar una suma arbitraria de scores. Primero definir constraints operacionales y después Pareto.

Ejemplo conceptual:

```text
maximize critical recall + macro F1
subject to false alarms/hour <= accepted limit
           latency p95 <= accepted limit
           CPU/RAM <= deployment budget
```

Los límites permanecen TARGET_CANDIDATE hasta medir.