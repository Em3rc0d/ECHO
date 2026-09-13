# Quarry — Privacy / Licensing

## Privacy baseline

```text
continuous audio
   ↓
short in-memory buffer
   ↓
classification/event decision
   ↓
discard by default
```

No ASR, no speaker ID, no voice profiling.

Event evidence clips solo si existe política/autorización explícita, con retention y ACL.

## Licensing baseline

Separar siempre:

```text
source code license
model/checkpoint license
dataset license
individual asset license
```

No usar “open source” como sinónimo de “sin restricciones”.

## Riesgos conocidos

- datasets NC;
- assets con licencias mixtas;
- checkpoints con condiciones distintas al repo;
- notices/attribution;
- redistribución de audio derivado de servicios externos.

Estado: `IN_PROGRESS`.