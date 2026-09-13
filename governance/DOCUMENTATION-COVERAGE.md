# Documentation Coverage Audit

**Status:** `ACTIVE`  
**Purpose:** impedir que ECHO vuelva a acumular Markdown stubs que parezcan decisiones terminadas.

## 1. Regla

Todo `.md` presente se clasifica como uno de:

```text
INDEX       navegación/README
KNOWLEDGE   investigación/evidencia
DECISION    diseño/arquitectura/política
PLAN        protocolo/secuencia
BUILD_SPEC  especificación de artefactos
TEST_SPEC   protocolo/criterios/resultados
LEDGER      trazabilidad/certificación
```

Ningún archivo sustantivo puede consistir únicamente en preguntas o bullets sin síntesis.

## 2. Minimum semantic content

Para `KNOWLEDGE`, `DECISION`, `PLAN`, `BUILD_SPEC` y `TEST_SPEC`, el reviewer debe poder encontrar:

```text
purpose
scope/non-scope
upstream dependencies
definitions
facts/evidence
alternatives/trade-offs
current decision/status
risks/failure modes
validation or measurement plan
downstream consumers
invalidation conditions
provenance/references
```

No existe mínimo rígido de palabras. La condición es reconstructibilidad.

## 3. Evidence tags

Usar cuando aclaren el estatus epistemológico:

- `FACT/EVIDENCE`
- `INFERENCE`
- `HYPOTHESIS`
- `DECISION`
- `TARGET`

Un `TARGET` nunca se presenta como resultado medido.

## 4. README policy

Un README puede ser más corto, pero debe explicar responsabilidad de la carpeta, estado, artefactos que contiene, inputs y salida hacia la siguiente fase. Un README de una frase no es aceptable.

## 5. Stub detector conceptual

Considerar sospechoso cualquier `.md` que tenga solo:

```text
preguntas
TODOs
una lista de nombres
un diagrama sin explicación
un status sin evidencia
```

Los stubs legítimos deben decir `STUB / NOT_CERTIFIED` y no pueden ser usados como input de un certificado.

## 6. Review cycle

Cada depth pass recorre root, governance, research, MK0, MK1 y MK2. Los artefactos demasiado superficiales se amplían antes de seguir al siguiente milestone.

## 7. Certification interaction

Expandir contexto sin cambiar semántica no invalida necesariamente una decisión. Cambiar decisión, contrato, taxonomy, metric protocol o dependency sí requiere revisar el DAG.

## 8. Completion criterion

El coverage audit se considera PASS cuando no quedan archivos sustantivos usados por gates cuyo contenido sea insuficiente para que otro ingeniero/agente reconstruya la decisión sin consultar el chat original.