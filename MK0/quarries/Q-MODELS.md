# Quarry — Models

## Preguntas

- ¿Qué modelo maximiza calidad bajo restricciones de CPU/latencia?
- ¿Embeddings frozen son suficientes?
- ¿Fine-tuning aporta valor con data de campo limitada?
- ¿Qué export formats son viables?
- ¿Qué licencia tiene código **y** checkpoint?

## Candidatos

```text
A YAMNet + ECHO head
B PANNs/Cnn14 + ECHO head
C ECHO CNN log-mel
D AST
E HTS-AT
F PaSST
G BEATs
```

## Cierre requerido

No elegir ganador hasta obtener un benchmark común con:

```text
same splits
same labels
same hardware
same streaming replay
same threshold calibration protocol
```

Estado: `IN_PROGRESS`.