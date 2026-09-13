# MK0 -> MK1 Handoff

**Status:** `CERTIFIED`

## Inputs inherited

Fixed promise/anti-scope; v1 taxonomy; multi-label semantics; data admission/group split/field-holdout rules; A/B/C benchmark; RTSP source abstraction; FFmpeg baseline; EventEngine lifecycle; MQTT/Mosquitto QoS1+idempotency; privacy/security baseline; risks and external camera gate.

## Empirical outputs MK1 must create

Model winner, per-class thresholds/calibration, source-hour false alarms, class misses, latency/resources, EventEngine parameters, logical multi-source capacity behavior, real-camera compatibility when accessible and first candidate SLOs.

## Frozen assumptions

MK1 implementation cannot silently change taxonomy, source identity, event semantics or test protocol simply to improve results. Such changes require version/re-audit.

## External gates

Camera model/audio/RTSP/codec/network/permission remain outside MK0 certification. Replay path exists so core build does not wait.

## Acceptance of handoff

`CERT-MK1-READY-001` confirms no architecture-changing OPEN item remains for replay build.

## Invalidation

If MK0 evidence is corrected materially, trace dependent MK1 artifacts through certification DAG.