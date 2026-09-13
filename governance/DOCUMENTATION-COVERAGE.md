# Documentation Coverage Audit

**Status:** `PASS_2026-09-13`  
**Purpose:** impedir que ECHO vuelva a acumular Markdown stubs que parezcan decisiones terminadas.  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-13.md`

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

Ningún archivo sustantivo puede consistir únicamente en preguntas, TODOs, nombres o bullets sin síntesis.

## 2. Minimum semantic content

Para `KNOWLEDGE`, `DECISION`, `PLAN`, `BUILD_SPEC` y `TEST_SPEC`, el reviewer debe poder reconstruir el subconjunto aplicable de:

```text
purpose / question
scope / non-scope
upstream dependencies
definitions
facts / evidence
alternatives / trade-offs
current decision / status
rationale
risks / failure modes
validation / measurement plan
downstream consumers
invalidation / closure conditions
provenance / references
```

No existe mínimo rígido de palabras. La condición es **reconstructibilidad**.

## 3. Evidence tags

Usar cuando aclaren el estatus epistemológico:

- `FACT/EVIDENCE`
- `INFERENCE`
- `HYPOTHESIS`
- `DECISION`
- `TARGET`

Un `TARGET` nunca se presenta como resultado medido.

## 4. README policy

Un README puede ser más corto porque su rol es `INDEX`, pero debe explicar responsabilidad de la carpeta, estado, artefactos/workstreams, inputs relevantes y salida hacia la siguiente fase. Un README de una frase no es aceptable.

## 5. Templates and future evidence

Un documento de evidencia futura puede ser compacto únicamente si declara explícitamente `TEMPLATE`, `NOT_CERTIFIED`, `PENDING_*` o estado equivalente y define qué campos/evidencia deben existir para cerrarlo. Un template nunca demuestra por sí mismo un resultado empírico.

## 6. Stub detector conceptual

Considerar fallo cualquier `.md` que tenga solamente:

```text
preguntas
TODOs
una lista de nombres
un diagrama sin explicación
un status sin significado o evidencia
claims empíricos sin medición
```

Los stubs legítimos deben decir `STUB / NOT_CERTIFIED` y no pueden ser usados como input de un certificado.

## 7. Último audit global

El audit del 2026-09-13 enumeró **174 Markdown existentes** en el baseline previo y agregó su propio ledger como el archivo 175. Distribución final:

| Zona | Markdown | Estado |
|---|---:|---|
| Root | 6 | PASS |
| Governance, incluyendo el audit ledger | 14 | PASS |
| Research | 5 | PASS |
| MK0 | 46 | PASS |
| MK1 | 54 | PASS |
| MK2 | 50 | PASS |
| **Total** | **175** | **PASS** |

Hallazgos de cierre:

- substantive certified-input stubs: `0`;
- question/TODO-only files posing as complete: `0`;
- status-only authoritative files: `0`;
- research final depth pass: committed;
- `GLOBAL_MD_AUDIT_2026_09_13 = PASS`.

El inventario archivo por archivo vive en `DOCUMENTATION-AUDIT-2026-09-13.md`.

## 8. Review cycle

Cada depth pass recorre root, governance, research, MK0, MK1 y MK2. Cualquier `.md` nuevo o materialmente reescrito entra nuevamente al audit. Los artefactos demasiado superficiales se amplían antes de usarse para un gate o una decisión downstream.

## 9. Certification interaction

Expandir contexto sin cambiar semántica no invalida necesariamente una decisión. Cambiar decisión, contrato, taxonomy, metric protocol, dependency, evidence basis o privacy policy sí requiere revisar `CERTIFICATION-DAG.md`.

## 10. Invalidation

El PASS global queda invalidado si:

- aparece un nuevo `.md` sin revisión/clasificación;
- un artefacto sustantivo se reemplaza por un stub;
- un documento certificado pierde provenance o rationale;
- cambia una decisión upstream y sus dependientes no se actualizan;
- el inventario real deja de coincidir con el ledger de cobertura.

## 11. Completion criterion

El coverage audit permanece PASS mientras no existan archivos sustantivos usados por gates cuyo contenido sea insuficiente para que otro ingeniero/agente reconstruya la decisión sin consultar el chat original.