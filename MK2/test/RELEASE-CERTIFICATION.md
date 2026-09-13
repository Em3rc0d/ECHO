# Release Certification — MK2

Una release recibe `CERTIFIED` sólo si:

- source commit/tree hash fijado;
- dependency/SBOM/license gates pasan;
- model package y data provenance cerrados;
- unit/integration/E2E pasan;
- regression ML pasa;
- load/soak/resilience pasan para el deployment profile;
- privacy/security checklist pasa;
- schemas compatibility validada;
- rollback probado;
- external gates aplicables cerrados.

El certificado referencia evidencia; no la duplica.