# Module Specification — MK1

Estructura prevista, no implementada:

```text
src/echo/
  domain/
    source.py
    audio.py
    inference.py
    events.py
  ingestion/
    base.py
    file.py
    rtsp.py
  audio/
    normalize.py
    window.py
  models/
    base.py
    yamnet.py
    panns.py
  event_engine/
    state.py
    policy.py
  messaging/
    mqtt.py
  telemetry/
    metrics.py
    logging.py
  app/
    runtime.py
```

El core depende de interfaces, no de FFmpeg/MQTT concretos. Esta estructura puede cambiar sólo mediante decision record antes de empezar build.