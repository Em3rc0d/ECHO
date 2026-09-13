# Audio Contract — MK1

## Canonical frame stream

Toda fuente se transforma antes de inferencia a un formato canónico.

```yaml
source_id: CAM-01
capture_ts: 2026-09-13T00:00:00.000Z
sample_rate_hz: 16000
channels: 1
sample_format: float32
range: [-1.0, 1.0]
sequence_no: 18422
```

El `sample_rate_hz` final queda sujeto al modelo ganador; 16 kHz es baseline compatible con YAMNet y DCASE baselines, no una ley universal.

## Window contract

Cada ventana incluye `window_id`, `source_id`, `start_ts`, `end_ts`, `samples`, `preprocess_version`. El overlap/hop se configura y versiona.

## Reglas

- downmix/resample ocurre una sola vez por pipeline;
- clipping, silencio prolongado y discontinuidades generan métricas;
- no se guarda PCM por defecto;
- timestamps de captura no se sustituyen por tiempo de inferencia;
- cualquier gap debe ser explícito, no rellenado silenciosamente sin policy.