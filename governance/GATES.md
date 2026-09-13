# Gates de ECHO

## Regla global

Ningún gate se certifica por intención. Requiere artefacto, evidencia verificable y dependencias válidas.

```text
MK0.BRAINSTORMING
      ↓
MK0.DESIGN
      ↓
MK0.ARCH
      ↓
MK0.PLAN
      ↓
MK0.BUILD (research tooling only, gated)
      ↓
MK0.TEST
      ↓
MK0 CERTIFIED
      ↓
MK1.BRAINSTORMING -> DESIGN -> ARCH -> PLAN -> BUILD -> TEST
      ↓
MK1 CERTIFIED
      ↓
MK2.BRAINSTORMING -> DESIGN -> ARCH -> PLAN -> BUILD -> TEST
      ↓
MK2 RELEASE CERTIFIED
```

## Estados

- `OPEN`: faltan decisiones/evidencia.
- `CANDIDATE`: propuesta plausible, todavía no certificada.
- `CERTIFIED`: criterios y dependencias satisfechos.
- `INVALIDATED`: cambió un input/dependencia.
- `EXTERNAL_GATE_OPEN`: depende de humano, hardware, red o credencial externa.

## Gate MK0 -> MK1

Debe existir y estar versionado:

- promesa/alcance IN/OUT;
- source catalog;
- matrices de proyectos/datasets/modelos;
- arquitectura target y PoC;
- contracts preliminares;
- taxonomía candidata y negativos;
- benchmark protocol;
- risk register;
- licensing registry;
- external gates explícitos;
- Definition of Ready MK1.

## Gate MK1 build

Además de MK0 certificado:

- clases MK1 congeladas;
- cámara/simulador definido;
- dataset manifest y splits definidos;
- baseline/challengers fijados;
- event lifecycle congelado;
- Pub/Sub contract congelado;
- test plan listo antes de implementar;
- secretos fuera de Git;
- criterios de aceptación marcados como TARGET/SLO/HYPOTHESIS según corresponda.

## Gate MK1 -> MK2

Requiere evidencia real de:

- ingestión estable;
- inferencia end-to-end;
- event aggregation;
- publicación Pub/Sub;
- métricas offline + streaming;
- error analysis;
- distance/SNR tests cuando hardware esté disponible;
- reconexión/failure behavior;
- decisión del modelo ganador o reasoned deferral.

## Gate MK2 release

Requiere multipunto real o carga equivalente reproducible, observabilidad, rollback, versionado de modelo/config/schema, tests de resiliencia, trazabilidad de artefactos y DoD cumplida.