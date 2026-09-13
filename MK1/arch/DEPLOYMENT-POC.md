# MK1 PoC Deployment

**Status:** `REFERENCE_DEPLOYMENT`

## Goal

Run the complete replay vertical on a developer/lab host with minimal operational dependencies, then substitute a real RTSP camera when external access closes.

## Logical deployment

```text
Host
  echo-app
    source supervisors
    decode/normalize
    model runner
    event engine
    publisher
    result API/store (minimal)

  Mosquitto

  subscriber/demo client

External or local assets
  dataset/replay files
  model/checkpoints
  optional IP camera on LAN/VPN
```

## Runtime packaging

Exact Python/runtime/container choice is a build decision but must be lockable/reproducible. FFmpeg can initially be a system/external binary whose version/build info is captured.

## Network

For replay, only local broker access is needed. For camera, host must reach authorized RTSP endpoint. Do not expose camera/broker publicly for convenience. Field security controls depend on actual network.

## Config/secrets

Non-secret config: source IDs, adapter type, model/config references, broker host/topic. Secrets: camera/broker credentials through environment/secret store; never committed.

## Persistence

MK1 may use lightweight local structured storage for events/results. It must be reproducible/exportable for tests and not rely on continuous audio retention.

## Failure expectations

Restart behavior, source reconnect and broker outage are explicit test cases. One process crash may interrupt PoC, but MK2 adds production supervision/HA if SLOs require it.

## Real-camera swap

`ReplaySource(SIM-01)` -> `RTSPSource(CAM-01)` changes adapter/config only. If downstream code changes, source abstraction failed.

## Invalidation

Change deployment reference if hardware/runtime profiling shows process separation is necessary before MK1 can meet its target envelope.