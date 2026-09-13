# MK1 Data Contracts

## Flujo

```text
SourceDescriptor
  -> AudioWindow
  -> RawInference
  -> CandidateEvent
  -> ConfirmedEvent
  -> AlertEnvelope
```

## SourceDescriptor

```json
{
  "schema_version": "echo.source.v1",
  "source_id": "CAM-001",
  "site_id": "SITE-001",
  "kind": "ip_camera",
  "stream_secret_ref": "secret://echo/cam-001",
  "enabled": true,
  "tags": ["north-gate"]
}
```

## RawInference

```json
{
  "schema_version": "echo.inference.v1",
  "window_id": "...",
  "source_id": "CAM-001",
  "stream_session_id": "...",
  "window_start_utc": "...",
  "window_end_utc": "...",
  "model": {"name": "echo-yamnet-head", "version": "0.1.0", "sha256": "..."},
  "scores": {"ALARM_SIREN": 0.84, "HORN": 0.05},
  "inference_ms": 18.4
}
```

## CandidateEvent

Existe mientras la evidencia temporal todavía no supera reglas de confirmación.

```json
{
  "schema_version": "echo.candidate.v1",
  "candidate_id": "...",
  "source_id": "CAM-001",
  "event_type": "ALARM_SIREN",
  "first_seen_utc": "...",
  "last_seen_utc": "...",
  "positive_windows": 2,
  "peak_score": 0.89,
  "state": "CANDIDATE"
}
```

## ConfirmedEvent

```json
{
  "schema_version": "echo.event.v1",
  "event_id": "...",
  "source_id": "CAM-001",
  "site_id": "SITE-001",
  "event_type": "ALARM_SIREN",
  "onset_utc": "...",
  "end_utc": "...",
  "confidence": {"peak": 0.94, "mean": 0.88},
  "model_version": "echo-yamnet-head@0.1.0",
  "threshold_version": "thresholds@0.1.0",
  "stream_session_id": "...",
  "provenance": {"input_hash": "...", "config_hash": "..."}
}
```

## AlertEnvelope

```json
{
  "schema_version": "echo.alert.v1",
  "alert_id": "...",
  "event_id": "...",
  "severity": "HIGH",
  "route": "mqtt",
  "created_utc": "..."
}
```

Schemas machine-readable preliminares viven en `/schemas/`.