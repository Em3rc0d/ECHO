# MK1 — First Build Specification

## Objetivo

MK1 define la primera vertical completa y científicamente evaluable de ECHO. Debe demostrar el pipeline de extremo a extremo con el menor scope físico razonable, sin sacrificar la arquitectura multi-source.

```text
brainstorming -> design -> arch -> plan -> build -> test
```

`mining-site/` y `quarries/` preservan la evidencia seleccionada y las preguntas que aún requieren benchmark.

## Scope de la primera build

PoC física permitida:

```text
1 cámara IP con audio
OR
1 micrófono/replay equivalente mientras el hardware esté EXTERNAL_GATE_OPEN
```

Arquitectura lógica obligatoria:

```text
N sources
```

## Vertical objetivo

```text
source
  ↓
decode/extract audio
  ↓
normalize/window
  ↓
model inference
  ↓
RAW_INFERENCE
  ↓
Event Engine
  ↓
CONFIRMED_EVENT
  ↓
MQTT Pub/Sub
  ↓
persistence/query/observability
```

## Estado

- brainstorming: DESIGNED
- design: IN_PROGRESS
- arch: IN_PROGRESS
- plan: IN_PROGRESS
- build: GATED_NOT_STARTED
- test: SPECIFIED_NOT_EXECUTED

MK1/build no se habilita hasta satisfacer `governance/DEFINITION-OF-READY.md`.