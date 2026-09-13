# MK1 Build Gate

**State:** `READY_NOT_STARTED`  
**Authorization:** `CERT-MK1-READY-001`

## Allowed first build

The first implementation may now execute the already-certified design in **offline/replay mode**:

```text
licensed/local test audio
  -> source adapter
  -> normalize 16 kHz mono contract
  -> window/buffer
  -> model A/B/C interface
  -> RAW_INFERENCE
  -> temporal Event Engine
  -> CONFIRMED_EVENT
  -> MQTT/Mosquitto publisher
  -> persistence/test subscriber
```

This gate does **not** authorize pretending that camera compatibility, distance, model winner, thresholds or SLOs have been proven.

## Real camera branch

Blocked by `EXT-CAMERA-001` until brand/model, audio availability, stream URI/access, codec, network and permission facts are captured.

## Build discipline

Implementation must trace every module/config/schema to a certified design artifact. Any architecture-changing discovery during build must reopen the upstream decision and invalidate dependent certification instead of being patched silently.