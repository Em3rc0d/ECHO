# MK2 Deployment Architecture

## Profiles

### Edge single-node

```text
ECHO runtime + broker + DB/embedded store
```

Adecuado a instalaciones pequeñas cuando capacidad lo permita.

### Split services

```text
edge ingest
   ↓ secure network
inference/event workers
   ↓
broker/store/api
```

Adecuado cuando N sources o hardware requieran separación.

## Containers

Containerization es candidato para reproducibilidad, no requisito conceptual. Si se adopta:

- images pinned by digest;
- SBOM/provenance future gate;
- model artifacts versioned separately;
- secrets mounted/injected, no baked.

## Health

```text
/liveness  -> process alive
/readiness -> dependencies/model/config ready
source health -> per source state
```

No declarar service ready si el modelo activo no está validado.