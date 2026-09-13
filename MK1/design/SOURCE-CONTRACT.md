# Source Contract — MK1

**Status:** `FROZEN_V1`

## Purpose

Represent an acoustic source without coupling downstream processing to RTSP, local microphone or file replay.

## Logical source

```yaml
source_id: stable unique id
site_id: optional logical site
source_type: replay|rtsp|microphone|nvr|other
enabled: bool
adapter_config_ref: non-secret configuration reference
secret_ref: optional external secret reference
metadata:
  device/model: optional
  location_label: optional non-sensitive logical label
```

## Stream session

Every connection/run creates `stream_generation` and emits samples/windows with sequence/timing metadata. This distinguishes a reconnect from the previous stream and prevents delayed old data from contaminating current event state.

## Source adapter responsibilities

Connect/open input; expose audio track; report original codec/rate/channels when known; emit decoded samples/timestamps; surface health/error states; respect cancellation/reconnect; never embed credentials into emitted domain objects.

## Downstream guarantee

The normalization/window pipeline receives source identity independently of adapter type. A replay and RTSP adapter must be interchangeable at that boundary.

## Health states

`DISABLED`, `CONNECTING`, `ONLINE`, `DEGRADED`, `RECONNECTING`, `OFFLINE`. Health is not acoustic classification; a connected silent/muted microphone may require a signal-quality warning.

## Failure behavior

Adapter errors are source-scoped. Reconnect uses bounded/backoff policy. Stale generation data is rejected.

## Security

No raw passwords in config/log/event payload. Secret references resolve at runtime.

## Validation

Contract tests use at least replay + fake/faulting adapter; real RTSP later proves hardware compatibility.

## Invalidation

Only reopen if a required source cannot express identity/session/audio/health through this abstraction.