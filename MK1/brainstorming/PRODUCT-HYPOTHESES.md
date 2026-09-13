# MK1 Product Hypotheses

**Status:** `ACTIVE_EXPERIMENT_SET`

## Purpose

Define what MK1 must learn empirically rather than treating expected behavior as fact.

| ID | Hypothesis | Measurement | Consequence if false |
|---|---|---|---|
| P-01 | at least one A/B/C model yields a useful quality/resource frontier | benchmark + replay | expand model/data research |
| P-02 | per-class thresholding + Event Engine makes continuous false alarms manageable | source-hour replay | revise aggregation/data/OOD |
| P-03 | public data plus hard-negative strategy supports initial five targets | class metrics/error analysis | shrink/remap classes |
| P-04 | normalized mono pipeline preserves target cues sufficiently | codec/sample-rate tests | revise audio contract/model path |
| P-05 | one runtime can isolate several replay sources | concurrency/fault test | change worker/process topology |
| P-06 | MQTT QoS1 + idempotency is operationally adequate for MK1 | reconnect/duplicate tests | add stronger delivery mechanism |
| P-07 | replay evidence predicts core behavior independent of camera adapter | replay vs camera comparison | bring hardware adaptation into core |
| P-08 | Event Engine parameters can be calibrated without test leakage | validation protocol | redesign temporal model/protocol |

## Measurement discipline

Each hypothesis has a pre-declared metric and failure interpretation. A disappointing result is useful evidence; do not tune the definition of success after seeing the test.

## Product decision link

P-01/P-02 produce model/threshold/event decisions. P-05 determines MK2 scale topology. P-07 is specifically gated on real-camera access.

## Invalidation

If taxonomy or metric definitions change, affected hypotheses/results are versioned and rerun.