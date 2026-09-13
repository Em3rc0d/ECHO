# MK1 / Plan

## Execution order after Ready

```text
1 contracts/config schemas
2 replay/file adapter
3 preprocessing/windowing
4 model baseline A
5 benchmark harness
6 challenger B/C
7 event engine
8 MQTT publisher
9 storage/query
10 RTSP adapter
11 observability
12 e2e/reconnect/replay tests
13 camera field test
14 MK1 certification
```

RTSP can move earlier if external camera access arrives, but the system is never allowed to skip offline benchmark/replay tests.

## No big-bang build

Cada slice debe conservar un contrato ejecutable:

```text
file -> inference
file -> event
file -> event -> mqtt
rtsp -> event -> mqtt
N replay sources -> scheduler -> events
```

## Version freeze antes de benchmark

Registrar:

```text
code git sha
dataset manifest sha
split manifest sha
model/checkpoint sha
training config sha
threshold config sha
runtime/environment
hardware profile
```

## Exit

MK1/test certifica la vertical; cualquier fallo importante vuelve al nodo upstream correspondiente.