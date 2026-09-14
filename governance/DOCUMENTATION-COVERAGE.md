# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-004`  
**Purpose:** impedir que ECHO acumule documentación profunda pero inconsistente, o Markdown stubs que parezcan decisiones terminadas.  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-13-CORPUS-CLOSURE.md`

## 1. Rule

Todo `.md` presente se clasifica conceptualmente como uno de:

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

La cobertura actual también exige **coherencia entre documentos**: un archivo individual puede ser profundo y aun así fallar si contradice una política superior o presenta estado histórico como current truth.

## 2. Minimum semantic content

Para `KNOWLEDGE`, `DECISION`, `PLAN`, `BUILD_SPEC` y `TEST_SPEC`, el reviewer debe poder reconstruir el subconjunto aplicable de:

```text
purpose / question
scope / non-scope
status / epistemic state
upstream dependencies
definitions
facts / evidence
alternatives / trade-offs
current decision
rationale
risks / failure modes
validation / measurement plan
downstream consumers
invalidation / closure conditions
provenance / references
ECHO-FREE-TIER-001 compatibility when execution is involved
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

Un documento de evidencia futura puede ser compacto únicamente si declara explícitamente `TEMPLATE`, `NOT_CERTIFIED`, `PENDING_*`, `OPEN` o estado equivalente y define qué campos/evidencia deben existir para cerrarlo. Un template nunca demuestra por sí mismo un resultado empírico.

## 6. Stub / contradiction detector

Considerar fallo cualquier `.md` que tenga solamente:

```text
preguntas
TODOs
una lista de nombres
un diagrama sin explicación
un status sin significado o evidencia
claims empíricos sin medición
```

También es fallo:

```text
current-state contradicts newer frozen policy
paid/self-hosted execution shown as required path under ECHO-FREE-TIER-001
historical certificate presented as current after invalidating changes
empirical node labelled complete without evidence
machine-readable policy and prose disagree materially
```

Los stubs legítimos deben decir `STUB / NOT_CERTIFIED` o equivalente y no pueden ser usados como input de un certificado.

## 7. Certificate lineage and corpus accounting

```text
CERT-DOC-001  historical / INVALIDATED for later corpus
CERT-DOC-002  historical / INVALIDATED-SUPERSEDED
CERT-DOC-003  historical / superseded for current HEAD
CERT-DOC-004  current / CERTIFIED
```

`CERT-DOC-003` covered **197 Markdown files** at commit `7ef9c1d52b12396e6e73f00f0a3a442d49061fe3`.

Since that certificate, the Corpus Foundry closure/free-tier work added seven substantive Markdown artifacts. The current governance pass also adds:

```text
+1 MK1 toolchain recertification record
+1 current documentation audit record
```

Therefore the current Markdown corpus represented by `CERT-DOC-004` is:

```text
197 + 7 + 1 + 1 = 206 Markdown files
```

Existing Markdown updated in place does not change the count.

The exact delta/coherence review is recorded in:

`governance/DOCUMENTATION-AUDIT-2026-09-13-CORPUS-CLOSURE.md`.

## 8. Current audit result

The current audit specifically reviewed the documentation changes caused by:

- Corpus Foundry Closure deep research;
- Corpus Solidity Gate;
- dataset source certification/materialization guidance;
- global `ECHO-FREE-TIER-001` governance;
- Foundry gate hardening;
- new toolchain recertification evidence;
- current-state and certification-DAG coherence.

Two meaningful coherence problems were corrected before promotion:

1. monolithic/self-hosted 120 GiB materialization guidance conflicted with the frozen global zero-cost boundary;
2. `CURRENT-STATE.md` still implied there were no remaining Foundry implementation/integration nodes although the new closure research had identified cross-format near-duplicate, hard-negative and final closure-integration work.

After correction, current documentation result is `PASS` for depth/reconstructibility/coherence.

This does **not** certify open empirical nodes such as `CERT-MK1-DF-CORPUS-001`, model winner, thresholds, capacity or field behavior.

## 9. Review cycle

Cada depth pass recorre root, governance, research, MK0, MK1 y MK2 as needed. Cualquier `.md` nuevo o materialmente reescrito entra nuevamente al audit. Los artefactos demasiado superficiales o contradictorios se corrigen antes de usarse para un gate o decisión downstream.

The preferred future mechanism is delta audit from the last documentation certificate, with full audit when dependency impact cannot be bounded confidently.

## 10. Certification interaction

Documentation is now a hard ancestor gate under `governance/CERTIFICATION-DAG.md`.

A certificate may close only when its governing documentation is current and its required technical/empirical evidence passes. Documentation and test evidence are complementary, not substitutes.

## 11. Invalidation

`CERT-DOC-004` becomes stale/invalid for current HEAD if:

- substantive Markdown is added or materially rewritten without review;
- an authoritative artifact regresses into a stub;
- a current document contradicts `PROJECT-CHARTER`, `ECHO-FREE-TIER-001`, machine-readable policy or another higher-precedence contract;
- a document certified as current loses provenance/rationale;
- a decision changes and dependent documentation is not updated;
- the 206-file inventory no longer represents the actual Markdown corpus.

## 12. Completion criterion

The documentation gate remains PASS only while another engineer/agent can reconstruct the current decision graph without consulting the original chat and without encountering unresolved contradictions presented as authoritative truth.