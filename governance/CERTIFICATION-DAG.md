# Certification / Evidence DAG

**Status:** `ARCHITECTURAL_POLICY_CERTIFIED`

## 1. Objetivo

ECHO necesita que cada decisión pueda reconstruirse y que una modificación upstream invalide automáticamente aquello que dependía de ella. La propiedad buscada se parece a una cadena de certificación, pero no necesita blockchain ni consenso distribuido.

## 2. Unidad de confianza

Cada nodo certificado representa un artefacto o claim con identidad, versión, inputs, outputs, criterios, evidence refs y hash. El commit Git conserva el estado histórico; manifests/CI podrán calcular hashes de archivos y artefactos externos.

## 3. Estado del nodo

```text
OPEN
CANDIDATE
CERTIFIED
INVALIDATED
EXTERNAL_GATE_OPEN
```

`CERTIFIED` siempre está acotado por scope. Por ejemplo, MK0 puede certificar el benchmark **protocol**, pero no el model winner que todavía no existe.

## 4. Manifest conceptual

```yaml
schema_version: echo.cert.v1
artifact_id: MK1-ARCH-001
artifact_version: 1.0.0
status: CERTIFIED
scope: replay-build architecture
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
invalidates_if:
  - source_contract changes
  - event_schema changes
certificate_sha256: ...
```

## 5. Dependency graph

```text
Promise
  -> problem boundary
  -> data/model/source evidence
  -> design contracts
  -> architecture
  -> plan/protocols
  -> build artifacts
  -> test evidence
  -> milestone certificate
```

Los quarries y mining-site proveen evidence nodes; las seis fases consumen y transforman esa evidencia.

## 6. Invalidation propagation

Si `taxonomy.v1` cambia a `taxonomy.v2`, se invalidan mappings, model heads, dataset manifests que dependan de labels, benchmark comparability, thresholds y event consumers que dependan de esos event types. No necesariamente se invalida RTSP ingest porque no depende de taxonomy.

La invalidación es **selectiva por dependencia**, no “todo el repositorio vuelve a cero”.

## 7. Git vs blockchain

Git ya provee content-addressed history para los archivos versionados. Para ECHO se necesitan además hashes de datasets/checkpoints/builds y attestations CI. No se necesitan minería, tokens, consenso BFT ni una red de validators.

## 8. Automatización futura

CI deberá:

```text
validate schemas
hash inputs/outputs
verify upstream certificates
reject INVALIDATED dependencies
produce build provenance
attach test result refs
sign release/model/container artifacts
update certification ledger
```

Herramientas como in-toto/SLSA/Sigstore pueden evaluarse en MK2, pero la arquitectura no depende de ellas hasta decidirlo.

## 9. Human review boundary

Claims científicos, licencias, privacy gates y cambios de scope pueden requerir revisión humana incluso si hashes/CI pasan. La automatización prueba integridad y reglas; no reemplaza juicio técnico.

## 10. Invalidation of the DAG itself

Reabrir este diseño si ECHO requiere múltiples repositorios no confiables, firmas externas obligatorias, compliance formal con un framework supply-chain específico o una organización distribuida que cambie el modelo de confianza.