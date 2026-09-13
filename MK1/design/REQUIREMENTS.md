# MK1 Requirements

**Status:** `FROZEN_FOR_REPLAY_BUILD`

## Functional requirements

`FR-01` Accept a configured logical source with stable `source_id`.  
`FR-02` Support deterministic file/replay input and later RTSP input behind the same adapter contract.  
`FR-03` Decode/normalize audio into the model input contract while retaining original-source metadata.  
`FR-04` Produce multi-label target probabilities for each analysis window.  
`FR-05` Attach model/preprocessing/config identity to inference evidence.  
`FR-06` Convert inference windows into candidate and confirmed events by source/type.  
`FR-07` Prevent cross-source Event Engine state leakage.  
`FR-08` Publish confirmed events through versioned MQTT topics/payloads.  
`FR-09` Provide a subscriber/persistence path sufficient for E2E verification.  
`FR-10` Emit health/runtime telemetry separate from acoustic events.  
`FR-11` Support replay of long positive/negative streams.  
`FR-12` Support multiple concurrent replay sources.  
`FR-13` Apply validation-derived per-class thresholds/config rather than hardcoded product truth.  
`FR-14` Expose unknown/no-target behavior rather than forcing a target class.  
`FR-15` Record reproducibility identifiers for benchmark/result bundles.

## Non-functional requirements

`NFR-01` Queues/buffers are bounded.  
`NFR-02` One source failure does not terminate unrelated sources.  
`NFR-03` Runtime lag/dropped windows are observable.  
`NFR-04` Secrets are external to Git and redacted from logs.  
`NFR-05` Continuous raw audio is not persisted by default.  
`NFR-06` Test data is frozen and isolated from training/calibration.  
`NFR-07` Benchmark runs are reproducible from commit/manifest/config/model hashes.  
`NFR-08` Contracts are schema/version aware.  
`NFR-09` ML quality is reported per class and operationally, not only aggregate accuracy.

## Target vs measured values

MK1 requirements define dimensions, not fictional thresholds. Numeric latency, false-alarm, recall and capacity limits are `TARGET_CANDIDATE` until first evidence allows freezing them.

## External requirements

Real camera validation needs `EXT-CAMERA-001`; replay build is independent. Field capture also requires authorization/retention policy.

## Acceptance mapping

Each requirement maps to `MK1/test/TEST-MATRIX.md`; a requirement is not DONE without an evidence artifact.

## Change control

A change that alters source identity, taxonomy or event semantics requires design/architecture recertification; implementation-detail changes may remain within build.