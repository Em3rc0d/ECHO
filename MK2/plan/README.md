# MK2 / Plan

## Entrada

MK1 `CERTIFIED` + error analysis + field/capacity evidence.

## Orden

```text
1 freeze MK2 SLOs
2 choose model winner + fallback
3 harden source lifecycle
4 bounded queues/backpressure
5 worker scheduler/batching
6 reliable publisher/idempotency
7 model/config registry
8 observability
9 provenance/attestation
10 rollback/release pipeline
11 load/soak/failure tests
12 field holdout
13 release certification
```

## Capacity ladder

Benchmark mínimo sugerido:

```text
1 source
4 sources
10 sources
N synthetic/replay stress (e.g. 25/50 if hardware allows)
```

No prometer N cámaras por servidor antes del benchmark.

## Model promotion

```text
candidate checkpoint
  ↓ offline gate
stream replay gate
  ↓ field holdout gate
runtime/capacity gate
  ↓ signed/hashed release
STAGED
  ↓ controlled activation
ACTIVE
```

## Release

Release incluye code + model + config + schemas + manifests, no solo un Git tag.