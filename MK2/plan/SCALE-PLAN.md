# Scale Plan — MK2

## Stage 1
1 host, múltiples replay sources; encontrar saturación.

## Stage 2
múltiples cámaras reales dentro de límites disponibles; comparar contra replay.

## Stage 3
worker pool/batching; medir throughput vs p95 latency.

## Stage 4
separar ingestion/inference sólo si profiling lo justifica.

## Capacity curve

Para N sources registrar CPU, GPU, RAM, queue depth, drops, RTF, p95/p99 latency y event throughput.

## Capacity declaration

Publicar capacidad certificada como `N sources @ codec/sample-rate/model/hardware/config`, nunca como número universal.