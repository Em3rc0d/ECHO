# Certification / Evidence DAG

## Objetivo

Implementar la propiedad conceptual solicitada de “cada paso valida/certifica al anterior” sin introducir blockchain innecesaria.

La unidad de confianza es un **artefacto certificado** con inputs, outputs, versión, hash, provenance, criterios y evidencia.

## Modelo

```text
Evidence/Inputs
    ↓
[artifact A]
    ↓ cert A
[artifact B references cert A]
    ↓ cert B
[artifact C references cert B]
    ↓ cert C
...
```

Un certificado downstream solo es válido si todos sus ancestros están válidos.

## Manifest mínimo

```yaml
schema_version: echo.cert.v1
artifact_id: MK1-ARCH-001
artifact_version: 1.0.0
status: CERTIFIED
stage: arch
milestone: MK1
inputs:
  - id: MK1-DESIGN-001
    sha256: <sha256>
outputs:
  - path: MK1/arch/ARCHITECTURE.md
    sha256: <sha256>
provenance:
  git_commit: <sha>
  generated_at_utc: <timestamp>
criteria:
  - id: AC-01
    result: PASS
evidence:
  - id: EV-001
    uri: <repo path or external source>
previous_certificate_sha256: <sha256-or-null>
certificate_sha256: <sha256>
```

## Invalidation

Si cambia `MK1-DESIGN-001`:

```text
MK1-DESIGN-001 v2
       ↓
MK1-ARCH-001 v1 -> INVALIDATED
       ↓
MK1-PLAN-001 v1 -> INVALIDATED
       ↓
MK1-BUILD-*       -> INVALIDATED
       ↓
MK1-TEST-*        -> INVALIDATED
```

No se borra el historial; se crea una nueva versión y se re-certifica el subgrafo afectado.

## Hash chain vs blockchain

ECHO necesita:

- integridad;
- provenance;
- reproducibilidad;
- firmas/attestations;
- invalidez transitiva.

No necesita:

- consenso distribuido;
- minería;
- token;
- red peer-to-peer de validadores.

Herramientas candidatas para MK2: in-toto attestations, Sigstore/Cosign y SLSA provenance. La decisión de implementación queda OPEN hasta MK2/plan.

## CI futura

La CI deberá poder:

1. calcular hashes de inputs/outputs;
2. validar JSON/YAML schemas;
3. verificar que dependencias estén `CERTIFIED`;
4. fallar si existe `INVALIDATED` upstream;
5. generar provenance del build;
6. firmar release/model/container;
7. bloquear activación de un modelo sin manifest válido.

No se implementa esta automatización mientras `build` permanezca gated.