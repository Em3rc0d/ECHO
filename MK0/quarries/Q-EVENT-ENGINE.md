# Quarry — Event Engine

## Problema

Los modelos puntúan ventanas. Los usuarios consumen eventos.

## Estado candidato

```text
IDLE
  ↓ score >= enter threshold
CANDIDATE
  ↓ temporal evidence M-of-N
ACTIVE / CONFIRMED
  ↓ score below exit threshold for K windows
CLOSED
  ↓ cooldown
IDLE
```

## Parámetros que NO se congelan todavía

```text
enter_threshold[class]
exit_threshold[class]
M/N
min_duration
max_gap
dedup_window
cooldown
severity routing
```

Todos deben derivarse de validation/stream replay.

## Métrica principal

`false alarms / source-hour` es tan importante como F1 offline.

Estado: `DESIGN_CANDIDATE`.