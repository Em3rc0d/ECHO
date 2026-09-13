# MK1 Code Structure Specification

**Status:** `FROZEN_BOUNDARIES / IMPLEMENTATION_PENDING`

## Proposed package layout

```text
src/echo/
  config/
  domain/
    source.py
    audio.py
    inference.py
    event.py
  sources/
    base.py
    replay.py
    rtsp.py
  audio/
    decode.py
    normalize.py
    window.py
  models/
    base.py
    yamnet.py
    panns.py
    compact_cnn.py
  runtime/
    supervisor.py
    scheduler.py
    workers.py
  events/
    engine.py
    state.py
  messaging/
    mqtt.py
  storage/
  observability/
  api_or_cli/
tests/
experiments/
configs/
```

Exact filenames may differ; responsibility boundaries should not.

## Dependency direction

Domain/contracts must not import FFmpeg/MQTT/framework-specific adapters. Sources depend on source contracts. Model adapters depend on model interface. EventEngine consumes inference domain records. Messaging consumes confirmed event contracts.

## Testability

Replay/fake adapters are first-class so core tests do not require network/hardware. Clock and ID generation should be injectable/deterministic where tests need them.

## Concurrency

Blocking decode/model work is isolated from control scheduling. State mutation occurs through clear ownership rather than global dictionaries shared unsafely.

## Configuration

No module reads arbitrary environment variables throughout code. Central config resolves validated settings/secret refs and passes typed configuration.

## Invalidation

If implementation requires circular dependencies or downstream modules to know adapter/model internals, architecture boundary needs review.