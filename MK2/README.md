# MK2 — Robust Product Specification

## Objetivo

MK2 convierte la vertical MK1 en un producto limpio, funcional, resiliente, multipunto y certificable dentro del alcance de ECHO.

**100% funcional** significa cumplir el scope, contratos, SLOs y Definition of Done aprobados. No significa 100% de accuracy ML.

## Pipeline interno obligatorio

```text
brainstorming -> design -> arch -> plan -> build -> test
```

Áreas transversales:

```text
mining-site/
quarries/
```

## MK2 no es “agregar features”

MK2 elimina fragilidades descubiertas por MK1:

- source scaling;
- backpressure;
- stream recovery;
- model/config/schema versioning;
- deployment reproducible;
- observability;
- signed provenance;
- rollback;
- load/soak/failure testing;
- field validation;
- privacy/security hardening.

## Estado

```text
brainstorming = SPECIFIED
 design      = SPECIFIED_CANDIDATE
 arch        = SPECIFIED_CANDIDATE
 plan        = SPECIFIED_CANDIDATE
 build       = GATED_NOT_STARTED
 test        = SPECIFIED_NOT_EXECUTED
```

MK2/build solo puede abrirse después de MK1 certificado.