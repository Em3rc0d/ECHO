# Dataflow — MK1

```text
[Source Adapter]
      |
 PCM chunks + timestamps
      v
[Per-source bounded buffer]
      |
 windows
      v
[Inference Adapter] ---> raw inference metrics
      |
 RAW_INFERENCE
      v
[Event Engine]
      |
 CONFIRMED_EVENT
      +----> [Event metadata store]
      |
      +----> [MQTT Publisher] ---> subscribers
```

## Backpressure PoC

Buffers deben ser acotados. Si el consumidor se retrasa, el pipeline registra drops/lag según policy; nunca crece memoria sin límite. Para audio en tiempo real suele ser preferible conservar datos recientes y marcar pérdida antes que procesar minutos atrasados como si fueran actuales, pero la política exacta se valida en tests.

## Ordering

Orden se garantiza por source dentro del proceso. No asumir orden global entre sources.