# Reference Architectures — MK0

**Status:** `CERTIFIED_BOUNDARIES`

## 1. Offline/replay architecture

```text
versioned audio assets
   -> ReplaySource(source_id)
   -> decode/normalize
   -> windows
   -> model runner
   -> RAW_INFERENCE
   -> Event Engine
   -> MQTT publisher
   -> test subscriber/event log
```

Purpose: deterministic development, benchmark and E2E testing without hardware dependency.

## 2. One-camera PoC architecture

```text
IP Camera/NVR
    -> RTSP
    -> FFmpeg
    -> normalized PCM
    -> same downstream pipeline as replay
```

The camera adapter must be replaceable with replay without modifying model/event contracts.

## 3. Target multi-source architecture

```text
CAM-01 --+
CAM-02 --+--> Source Supervisors -> per-source bounded buffers --+
FILE-N --+                                                   |
                                                            v
                                                fair inference scheduler
                                                            |
                                                     shared worker pool
                                                            |
                                                  RAW_INFERENCE records
                                                            |
                                          per-source/per-class Event Engine
                                                            |
                                                    confirmed event bus
```

## 4. Scale evolution

MK1 can run components in one host/process group. MK2 may split ingest, inference and event delivery into separate processes/hosts if profiling demonstrates need. The logical contracts remain unchanged.

## 5. Deployment alternatives

Edge/local deployment minimizes upstream raw-audio transfer and network dependency. Central inference can simplify model management and share accelerators across sources. Hybrid topology is valid if normalized source/event contracts remain explicit. ECHO does not freeze topology before capacity/security evidence.

## 6. Resilience principles

Source failure isolated; queues bounded; reconnect uses backoff; stale generation discarded; broker failure observable; model/config version attached to inference/event; health telemetry separate from event classification.

## 7. Validation

N deterministic replay sources validate logical scaling before claiming physical camera scale. Capacity claims require load/soak on target hardware.

## 8. Invalidation

Change reference architecture only when empirical constraints show the boundaries are inadequate, not merely because another framework is fashionable.