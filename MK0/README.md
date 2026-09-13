# MK0 — Research / Evidence Foundation

## Objetivo

MK0 convierte Internet, papers, repositorios, datasets, estándares y conocimiento del dominio en una base verificable para decidir qué construir.

**MK0 no es una PoC.** Su producto es reducción de incertidumbre.

## Pipeline interno obligatorio

```text
brainstorming -> design -> arch -> plan -> build -> test
```

Áreas transversales internas:

```text
mining-site/  # evidencia, claims, provenance
quarries/     # líneas de investigación/extracción
```

## Estado

| Fase | Estado | Criterio |
|---|---|---|
| brainstorming | IN_PROGRESS | problem space y escenarios consolidados |
| design | IN_PROGRESS | taxonomía/contratos/metrics candidates |
| arch | IN_PROGRESS | arquitectura target + tradeoffs |
| plan | IN_PROGRESS | benchmark/data/field protocol |
| build | GATED_NOT_STARTED | solo tooling de research después de cierre previo |
| test | NOT_STARTED | certifica MK0 y habilita MK1 |

## Salida esperada

MK0 termina cuando podemos responder sin improvisar:

- qué eventos vale la pena detectar;
- qué datos existen y bajo qué licencias;
- qué modelos deben benchmarkearse;
- cómo ingresa el audio;
- cómo se convierte una inferencia en evento;
- cómo se publica el evento;
- qué métricas deciden éxito;
- qué depende de hardware/cámara real;
- qué riesgos pueden matar el proyecto;
- qué decisiones siguen abiertas y por qué.

## Regla de evidencia

Cada afirmación relevante debe etiquetarse como `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS` o `DECISION_CANDIDATE`.

Ninguna hipótesis se convierte en requisito certificado por repetición.