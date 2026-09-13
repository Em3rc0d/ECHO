# MK2 Release Plan

## Release manifest candidate

```yaml
release: echo-1.0.0
code_git_sha: ...
schemas:
  event: echo.event.v1
model:
  name: echo-model
  version: 1.0.0
  sha256: ...
config:
  thresholds_sha256: ...
  event_engine_sha256: ...
dataset:
  manifest_sha256: ...
tests:
  report_sha256: ...
provenance:
  attestation_sha256: ...
```

## Certification

El release gate debe verificar:

- artifact hashes;
- ancestors certified;
- required test reports exist;
- active SLO set passed;
- no external release gate open;
- secrets absent;
- dependency/license inventory complete.

## Signing candidate

in-toto/Sigstore/Cosign se evalúan como herramientas de firma/attestation. No se diseña criptografía propia si una herramienta estándar satisface el objetivo.