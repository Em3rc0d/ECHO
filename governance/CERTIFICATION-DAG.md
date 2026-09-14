# Certification / Evidence DAG

**Status:** `ARCHITECTURAL_POLICY_CERTIFIED`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `governance/DOCUMENTATION-STANDARD.md`

## 1. Objetivo

ECHO necesita que cada decisión pueda reconstruirse y que una modificación upstream invalide automáticamente aquello que dependía de ella. La propiedad buscada se parece a una cadena de certificación, pero no necesita blockchain ni consenso distribuido.

La documentación es parte del sistema de confianza: ninguna evidencia empírica o CI verde compensa un contrato documental contradictorio, y ninguna documentación sólida compensa la ausencia de la evidencia requerida por un claim empírico.

## 2. Unidad de confianza

Cada nodo certificado representa un artefacto o claim con identidad, versión, inputs, outputs, criterios, evidence refs y hash. El commit Git conserva el estado histórico; manifests/CI calculan o podrán calcular hashes de archivos y artefactos externos.

Cada certificado debe poder responder, dentro de su scope:

```text
qué claim certifica
qué documentación normativa lo define
qué inputs certificados consume
qué criterios de aceptación usa
qué evidencia demuestra PASS
qué no certifica
qué lo invalida
cómo cumple ECHO-FREE-TIER-001
```

## 3. Estado del nodo

```text
OPEN
CANDIDATE
CERTIFIED
INVALIDATED
EXTERNAL_GATE_OPEN
```

`CERTIFIED` siempre está acotado por scope. Por ejemplo, MK0 puede certificar el benchmark **protocol**, pero no el model winner que todavía no existe.

## 4. Precondiciones universales de certificación

Un nodo no puede pasar a `CERTIFIED` si falla cualquiera de sus ancestros aplicables:

```text
promise/scope ancestor
        +
documentation coherence ancestor
        +
ECHO-FREE-TIER-001 ancestor
        +
required technical/empirical evidence ancestors
        ↓
certificate eligibility
```

En particular:

- documentación normativa stale/contradictoria -> `FAIL_DOCUMENTATION_GATE`;
- ejecución que requiere pago o overage -> `FAIL_FREE_TIER_GATE`;
- evidencia empírica ausente -> nodo empírico permanece `OPEN`;
- dependencia `INVALIDATED` -> dependiente no puede seguir `CERTIFIED` sin revalidación.

## 5. Manifest conceptual

```yaml
schema_version: echo.cert.v1
artifact_id: MK1-ARCH-001
artifact_version: 1.0.0
status: CERTIFIED
scope: replay-build architecture
documentation:
  - path: MK1/arch/ARCHITECTURE.md
    sha256: ...
  - certificate: CERT-DOC-...
free_tier_boundary:
  policy_id: ECHO-FREE-TIER-001
  result: PASS
inputs:
  - id: MK1-DESIGN-001
    version: 1.0.0
    sha256: ...
outputs:
  - path: MK1/arch/ARCHITECTURE.md
    sha256: ...
criteria:
  - id: ARCH-BOUNDARIES
    result: PASS
provenance:
  git_commit: ...
  generated_at_utc: ...
evidence:
  - id: EV-RTSP-001
    uri: ...
non_claims:
  - field performance
invalidates_if:
  - source_contract changes
  - event_schema changes
  - documentation ancestor becomes stale
  - free-tier policy is violated
certificate_sha256: ...
```

## 6. Dependency graph

```text
Immutable Promise
       |
       +--------------------+
       |                    |
       v                    v
Documentation Standard   Free-Tier Boundary
       |                    |
       +---------+----------+
                 |
                 v
        problem boundary
                 |
                 v
      data/model/source evidence
                 |
                 v
          design contracts
                 |
                 v
           architecture
                 |
                 v
          plan/protocols
                 |
                 v
          build artifacts
                 |
                 v
           test evidence
                 |
                 v
        milestone certificate
```

Los quarries y mining-site proveen evidence nodes; las seis fases consumen y transforman esa evidencia. La documentación de cada fase debe existir y ser coherente antes de que el claim downstream sea certificable.

## 7. Documentation certificate behavior

Los certificados de documentación (`CERT-DOC-*`) certifican profundidad/reconstructibilidad/coherencia del corpus documental para una versión concreta del repositorio.

Cuando aparece Markdown sustantivo nuevo, una política machine-readable cambia una verdad documentada o una decisión vigente deja obsoleto `CURRENT-STATE.md`, el certificado documental vigente deja de representar current HEAD y debe ser reemplazado mediante delta/full audit.

Esto no invalida automáticamente toda evidencia histórica; sí bloquea nuevos certificados que dependan de documentación no re-auditada.

## 8. Invalidation propagation

Si `taxonomy.v1` cambia a `taxonomy.v2`, se invalidan mappings, model heads, dataset manifests que dependan de labels, benchmark comparability, thresholds y event consumers que dependan de esos event types. No necesariamente se invalida RTSP ingest porque no depende de taxonomy.

Si cambia un documento sin cambiar semántica, puede bastar un documentation delta audit. Si cambia la semántica/contrato, se invalidan los dependientes técnicos correspondientes.

La invalidación es **selectiva por dependencia**, no “todo el repositorio vuelve a cero”.

## 9. Git vs blockchain

Git ya provee content-addressed history para los archivos versionados. Para ECHO se necesitan además hashes de datasets/checkpoints/builds y attestations CI. No se necesitan minería, tokens, consenso BFT ni una red de validators.

## 10. Automatización

CI debe evolucionar hacia:

```text
validate documentation governance
validate schemas
hash inputs/outputs
verify upstream certificates
reject INVALIDATED dependencies
verify ECHO-FREE-TIER-001
produce build provenance
attach test result refs
sign/attest release/model/container artifacts when justified by the zero-cost path
update certification ledger through reviewed evidence
```

Herramientas como in-toto/SLSA/Sigstore pueden evaluarse en MK2, pero la arquitectura no depende de ellas hasta decidirlo y deben respetar `ECHO-FREE-TIER-001`.

## 11. Human review boundary

Claims científicos, licencias, privacy gates, semantics y cambios de scope pueden requerir revisión humana incluso si hashes/CI pasan. La automatización prueba integridad y reglas; no reemplaza juicio técnico.

## 12. Invalidation of the DAG itself

Reabrir este diseño si ECHO requiere múltiples repositorios no confiables, firmas externas obligatorias, compliance formal con un framework supply-chain específico o una organización distribuida que cambie el modelo de confianza.