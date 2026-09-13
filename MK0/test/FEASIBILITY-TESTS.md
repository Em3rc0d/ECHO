# Feasibility Tests — MK0 to MK1

**Status:** `TEST_PROTOCOL_DEFINED / EXECUTION_SPLIT_ACROSS_MK1`

## Purpose

Define experiments needed to turn research assumptions into ECHO evidence.

## Data feasibility

Build a candidate manifest, filter by license/semantics, deduplicate/group and report unique groups per class. Failure: one or more target classes become too sparse/ambiguous for defensible evaluation.

## Model feasibility

Run A/B/C with common splits and report per-class metrics plus runtime. Failure: no candidate achieves a viable quality/resource frontier, triggering extended model research.

## Streaming feasibility

Replay continuous positives/negatives through windowing + Event Engine. Measure false alarms/source-hour, misses, fragmentation/duplicates and detection latency. Failure: clip quality does not translate to event quality.

## Multi-source feasibility

Run concurrent deterministic sources, inject one failure/noisy source, verify bounded memory, per-source state isolation and scheduler fairness.

## Delivery feasibility

Publish confirmed events through MQTT, test QoS1 duplicate behavior, reconnect and idempotent consumer handling.

## Camera feasibility

When external gate closes, probe RTSP/audio codec, decode stability, reconnect/jitter and signal quality. Compare with replay path using same downstream contracts.

## Privacy/security feasibility

Verify no secrets in logs/Git, no default persistent audio, temp/crash behavior and least-privilege broker/source access.

## Evidence bundles

Every test records commit, manifest/config/model hashes, environment, expected criteria, actual result and limitation.

## Gate interaction

Replay/model/data tests can proceed before hardware. Field claims remain blocked until camera/site evidence exists.