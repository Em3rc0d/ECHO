# MK1 Detailed Architecture

## Context

```text
IP Camera / Mic / Replay
          |
          v
        ECHO
          |
          +--> MQTT subscribers
          +--> Event query client
          +--> Metrics collector
```

## Source lifecycle

```text
REGISTERED
   ↓ connect
CONNECTING
   ├─success→ ONLINE
   └─fail────→ DEGRADED/OFFLINE
ONLINE
   ├─stalled→ DEGRADED
   └─closed─→ RECONNECT_WAIT
RECONNECT_WAIT
   ↓ backoff
CONNECTING
```

## Audio pipeline

YAMNet baseline path:

```text
camera codec
   ↓ decode
PCM/float
   ↓ mono mix
mono
   ↓ resample
16 kHz
   ↓ windowing
~0.96 s patches / ~0.48 s hop
   ↓
YAMNet embeddings
   ↓
ECHO multi-label head
```

Other models may own different preprocessing; therefore `Preprocessor` is model-profile-driven.

## Event lifecycle

```text
RawInference[n]
    ↓ per-class scoring
CandidateEvent
    ↓ temporal confirmation
ConfirmedEvent ACTIVE
    ↓ end criteria
ConfirmedEvent CLOSED
    ↓ publish/persist
Alert policy / analytics
```

## Pub/Sub

Topic candidate:

```text
echo/v1/{site_id}/{source_id}/events/{event_type}
```

Payload = `echo.event.v1`.

## Observability

Minimum metrics:

```text
source_online{source_id}
stream_reconnect_total{source_id}
audio_queue_depth{source_id}
window_total{source_id}
inference_seconds{model}
event_total{source_id,event_type}
publisher_failure_total
end_to_end_latency_seconds{event_type}
```

Minimum logs are structured JSON and must never contain stream passwords.