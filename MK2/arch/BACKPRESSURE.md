# Backpressure — MK2

Audio tiempo real no permite backlog infinito.

## Capas

1. socket/decoder buffer;
2. normalized chunk buffer;
3. window queue;
4. inference queue;
5. event delivery queue.

Cada capa tiene capacidad y política.

## Overload strategies a comparar

- drop oldest windows;
- adaptive hop/downsampling;
- per-source quotas;
- reject/new-source admission control;
- scale workers;
- temporary degraded mode.

## Invariante

Si se descarta audio, `data_gap`/metrics deben reflejarlo. Nunca presentar inferencia atrasada como si fuera detección actual.