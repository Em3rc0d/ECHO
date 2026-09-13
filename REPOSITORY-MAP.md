# ECHO Repository Map

Este mapa describe qué debe vivir en cada zona. La estructura es deliberadamente repetible para que cada milestone sea auditable.

```text
MK*/
├── brainstorming/  # problema, hipótesis, scope, escenarios
├── design/          # requisitos, contracts, taxonomy, policies
├── arch/            # componentes, dataflow, deployment, resilience
├── plan/            # research/build/eval/release sequencing
├── build/           # especificación + artefactos; gated hasta DoR
├── test/            # acceptance, regression, E2E, load/fault gates
├── mining-site/     # evidencia, sources, manifests, benchmark history
└── quarries/        # preguntas abiertas por dominio técnico
```

## MK0 — evidence first

Objetivo: reducir incertidumbre antes de construir. Sus artefactos documentan landscape, candidates, datasets, modelos, protocolos, riesgos y cómo se validará cada claim.

## MK1 — first vertical product

Objetivo: congelar una primera vertical sólida. Define source/audio/event contracts, pipeline, modelo mediante benchmark, Event Engine, Pub/Sub, observability, privacy y test suite antes de activar build.

## MK2 — robust product

Objetivo: convertir la vertical en producto multi-source operable: scaling, backpressure, durable delivery cuando el SLO lo exija, model governance, CI/CD, security, observability, load/soak/fault tests y release certification.

## Capas transversales

- `governance/`: gates, decision log, risk register, DoR/DoD, certification DAG.
- `research/`: matrices consolidadas de modelos/datasets/proyectos/fuentes.
- `schemas/`: contracts machine-readable compartidos.

## Regla de dependencia

Artefactos downstream deben enlazar inputs upstream. Si cambia una decisión certificada de la que dependen, su estado pasa a `INVALIDATED` hasta repetir la evidencia correspondiente.

## Regla de implementación

La existencia de `build/` no autoriza programar. `build` sólo se abre cuando brainstorming, design, arch y plan del milestone han alcanzado el gate definido y el test/acceptance plan ya está especificado.