# MK0 / Plan

## Orden de cierre

```text
1. Source catalog
2. Model landscape
3. Dataset/license landscape
4. Related-project analysis
5. Taxonomy candidate
6. Architecture tradeoffs
7. Event contracts
8. Benchmark protocol
9. Field protocol
10. Risk register
11. External gates
12. MK0 test/gate
```

## Benchmark A/B/C mínimo

- **A:** YAMNet embeddings + ECHO head.
- **B:** PANNs/Cnn14 transfer baseline.
- **C:** CNN propia sobre log-mel como control.

Extended benchmark: AST/HTS-AT/PaSST/BEATs si el presupuesto de MK1 lo permite o en MK2.

## Dataset plan

1. crear registry de datasets;
2. registrar licencia por asset cuando aplique;
3. mapear labels a taxonomía ECHO;
4. extraer hard negatives;
5. crear group-aware splits;
6. reservar field holdout;
7. no commit de audio raw.

## Metrics plan

Offline:

```text
precision/recall/F1 per class
macro/micro F1
PR-AUC
calibration
```

Streaming:

```text
false alarms / source-hour
missed events
onset->event latency p50/p95/p99
CPU/RAM
throughput windows/s
queue lag
reconnect count
```

Robustez:

```text
recall vs distance
F1/recall vs SNR
performance vs microphone/codec/site
```

## Distance protocol candidate

Evaluar, cuando sea seguro y autorizado:

```text
5 m
10 m
15 m
20 m
25 m
```

No se fabrican eventos peligrosos. Para eventos no seguros se utiliza audio autorizado/replay controlado o capturas pasivas.

## Gate

`MK0/test/MK0-GATE.md` decide si MK1 puede pasar a build.