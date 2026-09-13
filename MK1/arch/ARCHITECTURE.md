# MK1 Reference Architecture

**Status:** `FROZEN_FOR_REPLAY_BUILD`

## 1. Context

ECHO receives audio from one or more logical sources, classifies target acoustic events and publishes structured confirmed events. MK1 is deployable on one host but architected so source/model/publisher boundaries can later split.

## 2. Component flow

```text
Replay / RTSP / Mic
        |
        v
SourceRegistry + SourceSupervisor
        |
        v
Decoder / Normalizer
        |
        v
bounded AudioBuffer[source_id]
        |
        v
WindowProducer
        |
        v
InferenceScheduler ----> ModelRunner(A|B|C)
        |                       |
        +<-- RAW_INFERENCE -----+
        |
        v
EventEngine[source_id,event_type]
        |
        v
ConfirmedEvent
     /      \
    v        v
MQTT       Event/Result Store
    \        /
      subscribers
```

## 3. Process boundaries

MK1 can begin as one application process plus external Mosquitto and model/runtime dependencies. Blocking decode/inference work must not freeze an async control loop; executor/worker boundaries are implementation details. Source adapters are independently supervised.

## 4. State ownership

SourceSupervisor owns connection/session. AudioBuffer owns bounded samples. Scheduler owns pending work/fairness. ModelRunner is stateless or concurrency-safe by contract. EventEngine owns temporal state keyed by source/type. Publisher owns delivery attempts, not event truth.

## 5. Data contracts

Only normalized audio/window internal objects and versioned inference/event schemas cross boundaries. Raw model tensors do not leak into Pub/Sub. Credentials do not cross source-adapter boundary.

## 6. Failure domains

One source decoder may reconnect without resetting others. Model failure marks affected work and surfaces health. Broker failure leaves detection observable and can buffer/retry only under explicit bounded policy. No component uses unbounded memory to “guarantee” delivery.

## 7. Deployment assumptions

PoC prefers local/LAN processing. Cloud is optional later. External broker/process versions are pinned in run manifests. Replay is deterministic and remains first-class even after RTSP integration.

## 8. Capacity

No source-count claim is frozen. N-replay tests profile queue lag, utilization, drops and event latency. MK2 determines scale topology from those results.

## 9. Security/privacy

Least privilege, external secrets, no default audio persistence, model/checkpoint hashes and broker access controls for non-lab deployment.

## 10. Invalidation

A change to source/audio/event contract or evidence that one-process boundaries cannot meet MK1 operating constraints triggers architecture review.