# Hypotheses Register — MK0

**Status:** `ACTIVE / ARCHITECTURE-CHANGING HYPOTHESES RESOLVED`

## Purpose

The register prevents assumptions from silently becoming requirements or “facts”. Each hypothesis records why it matters, how it can be tested and whether its uncertainty blocks build.

| ID | Hypothesis | Current state | Test/evidence path | If false |
|---|---|---|---|---|
| H-01 | pretrained acoustic representations outperform or simplify a small from-scratch model | EMPIRICAL | A/B/C benchmark | select custom model or another backbone |
| H-02 | five MK1 target classes can be supported by licensed/diverse data | CONTROLLED | asset manifest + class mapping | shrink/rename taxonomy before affected training |
| H-03 | per-class thresholds reduce operational false alarms vs a fixed global threshold | EMPIRICAL | validation PR curves + replay | use alternative calibration/event logic |
| H-04 | a temporal Event Engine reduces duplicate/fragmented alerts | EMPIRICAL | streaming replay ablation | redesign aggregation |
| H-05 | RTSP abstraction is sufficient for likely IP-camera integration | EXTERNAL_VALIDATION | camera probe | add NVR/vendor adapter without changing core source contract |
| H-06 | 16 kHz mono normalized audio preserves enough signal for baseline targets | EMPIRICAL | codec/sample-rate ablation | adjust audio contract/model path |
| H-07 | replay can validate most core behavior before camera access | ACCEPTED | deterministic source adapter design | camera dependency moves earlier |
| H-08 | bounded worker scheduling can support multiple concurrent sources without state leakage | EMPIRICAL | N-replay load tests | revise worker/process architecture |
| H-09 | public datasets alone cannot certify field performance | STRONGLY_SUPPORTED | domain evidence + field plan | if field matches unexpectedly, holdout still remains required for claim |
| H-10 | raw continuous audio is unnecessary for normal product operation | DESIGN_DECISION | event/telemetry contract | retention policy must reopen if later feature requires media |
| H-11 | MQTT QoS1 + idempotent consumers is sufficient for MK1 | EMPIRICAL | duplicate/reconnect tests | add durability/outbox or alternate bus in MK2 |
| H-12 | simple abstention + hard negatives may be more useful than complex OOD in MK1 | EMPIRICAL | unknown/negative replay | investigate embedding/OOD methods |

## Closure rules

A hypothesis becomes `DECISION` only after either evidence or a product constraint justifies freezing it. Intrinsically measurable quantities remain empirical outputs instead of being “closed” by research.

## Priority

H-02, H-05/H-06, H-08 and H-11 can force implementation changes and therefore receive early tests. Model-winner and threshold hypotheses are expected outputs of MK1 and do not block build.

## Invalidation

New evidence, a taxonomy change, new camera hardware or a deployment constraint can reopen a hypothesis. Historical states remain traceable through Git.