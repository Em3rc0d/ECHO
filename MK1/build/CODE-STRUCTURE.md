# Planned Code Structure — MK1

**Especificación; no creada todavía como código ejecutable.**

```text
src/echo/
├── domain/
│   ├── source.py
│   ├── inference.py
│   ├── event.py
│   └── alert.py
├── ingest/
│   ├── base.py
│   ├── file.py
│   ├── microphone.py
│   └── rtsp_ffmpeg.py
├── audio/
│   ├── normalize.py
│   ├── window.py
│   └── buffer.py
├── inference/
│   ├── base.py
│   ├── scheduler.py
│   ├── yamnet.py
│   ├── panns.py
│   └── custom_cnn.py
├── events/
│   ├── engine.py
│   ├── state.py
│   └── thresholds.py
├── messaging/
│   ├── base.py
│   └── mqtt.py
├── storage/
│   ├── repository.py
│   └── models.py
├── api/
│   └── app.py
├── observability/
│   ├── metrics.py
│   └── logging.py
├── provenance/
│   └── manifest.py
└── config/
    └── settings.py

tests/
├── unit/
├── integration/
├── e2e/
├── replay/
└── fixtures/

configs/
├── labels.yaml
├── thresholds.yaml
├── event-engine.yaml
├── sources.example.yaml
└── models.yaml
```

## Dependency direction

```text
domain <- adapters
```

El dominio no importa FFmpeg, MQTT, TensorFlow/PyTorch ni DB drivers. Esto permite reemplazar infraestructura/modelos sin contaminar contratos core.