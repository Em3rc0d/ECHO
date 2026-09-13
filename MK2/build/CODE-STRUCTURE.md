# MK2 Code Structure Target

**Status:** `TARGET_SPEC`

## Evolution from MK1

Keep domain/source/audio/model/event/messaging boundaries. Add production services only where needed: model registry/client, durable event outbox/store if selected, metrics/tracing adapters, admin/health APIs, deployment/migration tooling and security policy modules.

## Possible service split

```text
ingest/source service(s)
inference service/worker(s)
event-engine/publisher
api/event query
```

This is a logical option, not mandatory microservices. A single deployable can still host several modules when capacity/availability allows.

## Dependency rule

Domain contracts remain framework-independent. Infrastructure modules depend inward, never the reverse. Model registry/deployment code cannot change event semantics silently.

## Shared schemas

Machine-readable contracts live in shared versioned package/schema directory and are tested across producers/consumers.

## Operations code

Health, metrics, migration, rollback and graceful shutdown are product code, not afterthought scripts.

## Invalidation

Final structure follows selected MK2 topology; preserve responsibility boundaries even if process split changes.