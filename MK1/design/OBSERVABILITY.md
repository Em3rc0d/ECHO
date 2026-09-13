# Observability — MK1

**Status:** `MINIMUM_SET_FROZEN`

## Purpose

Make failures and performance measurable without requiring raw-audio retention or leaking secrets.

## Source metrics

Connection state, last packet/sample/window/inference timestamps, stream generation, reconnect count, decode errors, signal-level/silence indicators where useful, buffer fill and queue lag/drop counts.

## Model/runtime metrics

Inference count, latency histogram p50/p95/p99, model ID/version, worker queue depth, throughput, CPU/GPU/RAM snapshots during benchmark and failed inference count.

## Event metrics

Candidates, confirmed/closed events by type/source, confirmation latency, duplicate/fragmentation diagnostics, false-positive/miss labels in evaluation mode and MQTT publish result/retry counters.

## Logging

Structured logs include source_id/event_id/inference_id as appropriate, severity, error category and safe configuration version. Redact credentials/RTSP userinfo and never log raw PCM.

## Health

Process health is not source health. Broker health is not model health. Expose separate states so one dependency failure is diagnosable.

## Cardinality/privacy

Avoid raw URLs, free-form user/location data and unbounded event IDs as metric labels. IDs belong in logs/traces; metrics use bounded dimensions where practical.

## Validation

Fault injection should produce the expected telemetry for stream failure, decoder error, queue overload, model exception and broker outage.

## MK2 evolution

Central metrics/tracing/alerting stack is deferred; MK1 focuses on structured data sufficient to prove behavior and diagnose experiments.