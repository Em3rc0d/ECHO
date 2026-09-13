# Observability — MK1

## Métricas por source

- `source_up`;
- `last_audio_age_seconds`;
- `decode_errors_total`;
- `reconnects_total`;
- `buffer_depth_seconds`;
- `windows_processed_total`;
- `windows_dropped_total`.

## Inferencia

- latency histogram p50/p95/p99;
- real-time factor;
- score distribution por clase;
- model errors;
- CPU/RAM/GPU.

## Event Engine

- candidates created/expired;
- confirmed events;
- deduplicated windows;
- cooldown suppressions;
- events por clase/source.

## Pub/Sub

- publish latency;
- failures/retries;
- duplicate deliveries observadas por subscriber test.

## Logging

Logs estructurados con `source_id`, `event_id`, `component`, `version`, sin secrets ni PCM.