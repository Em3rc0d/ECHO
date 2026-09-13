# System Boundary — MK0

**Status:** `CERTIFIED`

## 1. ECHO owns

ECHO owns the logical pipeline from an authorized audio source through normalization, inference and temporal event formation to a structured event interface. It owns source identity propagation, model/config versions, event confidence, health signals needed for acoustic processing and the rules that prevent raw windows from becoming duplicate alerts.

## 2. External systems

Cameras/NVRs provide streams; networks transport packets; brokers route events; dashboards/mobile clients render or act on events; human operators may validate context. These are external dependencies even when the PoC deploys them in one machine.

## 3. Boundary diagram

```text
[Camera/NVR/Mic/File]
       |
       | authorized audio
       v
+---------------- ECHO ----------------+
| source adapter                        |
| decode / normalize / buffer           |
| windowing / inference                 |
| calibration / abstention              |
| temporal Event Engine                 |
| event contract + health telemetry     |
+----------------+----------------------+
                 |
        structured event/telemetry
                 v
        [Broker/API/Store/UI]
```

## 4. Data ownership

The audio stream is an input, not automatically a retained ECHO asset. By default only ephemeral samples/features and structured metadata are required. Field clips become dataset assets only under an explicit authorized evaluation manifest.

## 5. Trust boundaries

Credentials enter through runtime secret configuration. Untrusted/remote network streams are decoded through constrained adapters. Model/checkpoint files are hash/provenance validated. Downstream consumers must not be able to mutate historical inference evidence silently.

## 6. Non-goals

ECHO does not own camera firmware management, video storage, incident adjudication, identity recognition or user-notification UX as core ML functionality.

## 7. Downstream design consequences

This boundary creates a `SourceAdapter`, normalized audio contract, inference envelope, Event Engine and publisher interface. It also enables file/replay sources to exercise the core without real hardware.

## 8. Validation

Use architecture tests to show the same downstream pipeline accepts a replay adapter and a real RTSP adapter without changing classifier/event contracts.

## 9. Invalidation

Reopen if a required feature demands raw media retention, bidirectional camera control, cross-modal video fusion inside the core, or another source type that cannot fit the abstraction.