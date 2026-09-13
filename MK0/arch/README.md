# MK0 / Arch

## Arquitectura target

```text
CAM/MIC-01 ─┐
CAM/MIC-02 ─┼──> Source Registry
CAM/MIC-N  ─┘         |
                       v
                Ingestion Adapters
                RTSP / file / mic
                       |
                       v
                Decode / Normalize
                 mono / 16 kHz*
                       |
                       v
             bounded buffer per source
                       |
                       v
               Inference Scheduler
                /       |       \
          worker A  worker B  worker N
                       |
                       v
                 ModelScores
                       |
                       v
                Event Engine
       threshold + temporal smoothing
       hysteresis + dedup + cooldown
                       |
                       v
                 AcousticEvent
                  /          \
                 v            v
             Event Store    MQTT/Event Bus
                               |
                               v
                        Subscribers/Alerts
```

`*` 16 kHz es baseline natural para YAMNet; no se convierte en requisito universal del dominio si otro modelo requiere otra entrada.

## Ingestión

`DECISION_CANDIDATE`:

- RTSP como primary path para cámara IP;
- ONVIF como discovery/config helper;
- FFmpeg como decoder/normalizer baseline;
- go2rtc solo si fan-out/reconnect/codec bridging lo justifica.

## Aislamiento por source

Cada source mantiene:

```text
stream_session_id
bounded ring buffer
health state
last frame timestamp
reconnect state
queue lag
```

Una fuente caída no debe bloquear las demás.

## Scheduling

No usar colas ilimitadas. Target MK2:

```text
bounded source queues
      ↓
fair scheduler
      ↓
optional micro-batches
      ↓
N inference workers
```

## Messaging

MQTT es candidato MK1 por simplicidad y Pub/Sub. ECHO debe diseñar idempotencia porque QoS 1 permite duplicados.

## Arquitectura PoC

```text
CAM-01 or replay
   ↓
FFmpeg/file adapter
   ↓
normalized windows
   ↓
model baseline
   ↓
Event Engine
   ↓
MQTT + event log
```

La PoC es unipunto físicamente; los contratos siguen siendo multi-source.