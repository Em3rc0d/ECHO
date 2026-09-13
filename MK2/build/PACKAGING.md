# Packaging — MK2

Candidates: Python package + container image para runtime reproducible.

## Requisitos

- pinned runtime base;
- FFmpeg version declarada;
- healthcheck;
- non-root cuando sea viable;
- model mounted/versioned separadamente o incluido con checksum;
- config/secret separation;
- deterministic dependency lock;
- SBOM/notices.

No congelar registry/cloud provider hasta conocer entorno de despliegue.