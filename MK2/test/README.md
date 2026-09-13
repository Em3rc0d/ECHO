# MK2 / Test

MK2/test certifica producto operacional, no solo funciones.

## Suites

```text
regression ML
contract compatibility
multi-source e2e
load
stress
soak
backpressure
reconnect
broker/storage failure
model rollback
config rollback
privacy/retention
provenance verification
field holdout
```

## Long-running

Soak test debe descubrir leaks, drift de latency, reconnect churn y acumulación de colas que un test corto no muestra.

## Failure injection

Probar de forma controlada:

- kill/restart worker;
- drop source network;
- broker unavailable;
- storage unavailable;
- corrupt/invalid model metadata;
- invalid config;
- duplicate messages;
- clock discontinuity simulation.

## Release test

Un release solo es válido si puede instalarse/reproducirse desde manifests y los artifacts exactos.