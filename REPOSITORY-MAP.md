# ECHO Repository Map

**Status:** `ACTIVE_ARCHITECTURAL_INDEX`

## 1. Propósito

Este documento explica no solo dónde está cada archivo, sino qué responsabilidad semántica tiene cada zona y cómo se mueve evidencia entre milestones. ECHO usa una estructura repetible para que una persona o agente pueda reconstruir el proyecto sin depender del historial del chat.

## 2. Estructura obligatoria por milestone

```text
MK*/
├── brainstorming/
├── design/
├── arch/
├── plan/
├── build/
├── test/
├── mining-site/
└── quarries/
```

El pipeline ejecutable es siempre:

```text
brainstorming -> design -> arch -> plan -> build -> test
```

`mining-site` y `quarries` alimentan las fases, pero no alteran ese orden.

## 3. Semántica de carpetas

### brainstorming

Preserva el problema, alternativas, hipótesis, anti-scope, escenarios y qué debe aprenderse antes de diseñar. No debe ocultar incertidumbre bajo decisiones prematuras.

### design

Convierte conocimiento en requisitos, contratos, taxonomías, políticas, invariantes y decisiones de comportamiento observables. Define **qué** debe hacer ECHO y qué significa cada dato.

### arch

Define **cómo se separan responsabilidades**: componentes, procesos, dataflow, concurrency, deployment, failure boundaries, source isolation, broker boundaries y resiliencia.

### plan

Ordena experimentos e implementación: datasets, benchmark, training, integration, field test, rollback, capacity y release. Toda métrica se define antes de medirla.

### build

Contiene la especificación de artefactos construibles y, una vez abierto el gate, la materialización correspondiente. La carpeta puede existir aunque el build esté `GATED`.

### test

Contiene criterios de aceptación, matrices, benchmark result expectations, E2E, seguridad, resiliencia, load/soak y certificados. Test no inventa resultados; almacena evidencia reproducible.

### mining-site

Es el almacén de evidencia y provenance: fuentes web, releases, licencias, manifests, benchmark history, field evidence e incident evidence.

### quarries

Son líneas de extracción de conocimiento. Cada quarry sigue `question -> evidence -> synthesis -> decision -> validation -> closure/invalidation`.

## 4. Milestones

### MK0 — Evidence first

Cierra incertidumbre de estado del arte, datos, modelos, ingestión, Pub/Sub, privacy, seguridad y benchmark. Puede certificar el **protocolo**, no resultados que aún no fueron medidos.

### MK1 — First vertical

Construye y prueba una vertical `source/replay -> audio -> model -> event engine -> MQTT -> consumer`. Debe producir modelo ganador, thresholds, métricas y evidencia de fallos.

### MK2 — Robust product

Convierte la vertical en producto multipunto operable: capacity, backpressure, recovery, observability, model governance, secure delivery, CI/CD, rollback y release certification.

## 5. Capas transversales

`governance/` mantiene decisiones, gates, riesgos y certificados. `research/` consolida el conocimiento técnico externo. `schemas/` contiene contratos machine-readable. Root contiene charter, estado y políticas de distribución.

## 6. Regla de enlaces

Todo artefacto sustantivo debe declarar o poder inferir:

```text
upstream inputs
current status
claims/decisions
validation plan
downstream consumers
invalidation conditions
references/provenance
```

## 7. Regla anti-stub

Un `.md` de ingeniería no se considera completo por tener título y preguntas. Si solo enumera tareas, debe estar marcado `STUB / NOT_CERTIFIED`. Los README pueden ser más compactos, pero deben explicar navegación, estado y dependencia.

## 8. Regla de certificación

Cambios materiales upstream invalidan certificados downstream. El historial no se reescribe: se crea una nueva versión, se actualiza el ledger y se recertifica el subgrafo afectado.