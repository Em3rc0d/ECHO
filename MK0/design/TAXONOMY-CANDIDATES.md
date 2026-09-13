# Taxonomy Candidates — MK0

La taxonomía todavía no está congelada. Se evalúa por observabilidad acústica, disponibilidad de datos, confusabilidad y valor para demo.

| Clase candidata | Señal acústica | Riesgo principal | Prioridad investigación |
|---|---|---|---|
| `GLASS_BREAK` | transiente de alta energía / fragmentación | platos/metal/chirridos | alta |
| `SIREN_ALARM` | patrón tonal/temporal repetitivo | música/alarmas domésticas | alta |
| `VEHICLE_COLLISION` | impacto complejo | portazos/obras/golpes | alta |
| `HORN` | señal tonal breve | sirena/música/tráfico | media-alta |
| `TIRE_SQUEAL` | energía sostenida alta frecuencia | maquinaria/frenos | media |
| `SCREAM_SHOUT` | voz humana de alta energía | juego/deporte/canto | media, sensible |
| `IMPACT` | transiente genérico | semántica ambigua | media |
| `OTHER_BACKGROUND` | resto del mundo acústico | heterogeneidad extrema | obligatoria |

## Criterios para congelar MK1

- positivos suficientes y legalmente utilizables;
- separación acústica razonable;
- hard negatives identificables;
- consistencia de mapeo entre ontologías;
- capacidad de validación con audio real;
- no exigir inferir intención o contexto social.

La taxonomía final de MK1 puede ser menor que esta lista.