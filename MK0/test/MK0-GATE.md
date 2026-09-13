# MK0 Gate Record

**Estado:** `CERTIFIED`  
**Certificate:** `CERT-MK0-013`  
**Scope:** investigación, decisiones de diseño y handoff a MK1. No certifica performance empírica.

## Criterios

| Gate | Estado | Evidence |
|---|---|---|
| G0-01 Promise/scope frozen | PASS | PROJECT-CHARTER + CERT-ECHO-000 |
| G0-02 Research source catalog | PASS | source catalog + WEB-AUDIT-2026-09-13 |
| G0-03 Related projects matrix | PASS | Frigate + related systems evidence |
| G0-04 Dataset matrix | PASS | AudioSet/FSD50K/SONYC/ESC/DCASE audit |
| G0-05 Model matrix | PASS | YAMNet/PANNs/control + extended candidates |
| G0-06 Architecture target/PoC | PASS | RTSP abstraction + multi-source boundary |
| G0-07 Event lifecycle/contracts | PASS | RAW -> CANDIDATE -> CONFIRMED -> ALERT |
| G0-08 Taxonomy final MK1 | PASS | TAXONOMY.md v1 frozen |
| G0-09 License policy for selected assets | PASS_WITH_MANIFEST_RULE | per-asset license mandatory; no raw asset without license record |
| G0-10 Camera external gate | EXTERNAL_GATE_OPEN | does not block replay build; blocks real-camera certification |
| G0-11 Benchmark protocol frozen | PASS | BENCHMARK-PROTOCOL.md v1 |
| G0-12 MK1 DoR | PASS_FOR_REPLAY_BUILD | real camera remains separate external branch |

## Certification boundary

MK0 is certified because all **architecture-changing research decisions** needed for the first build have been closed. The following remain intentionally empirical and therefore do not invalidate MK0:

- winner A/B/C;
- thresholds;
- measured accuracy/recall/F1;
- latency/runtime;
- distance/SNR;
- final SLOs;
- real-camera characteristics.

Those are outputs of MK1 build/test, not prerequisites that can be truthfully known in MK0.

## Consequence

```text
MK0 = CERTIFIED
MK1/build replay/offline = READY_NOT_STARTED
MK1 real-camera certification = EXTERNAL_GATE_OPEN
MK1 overall certification = NOT_YET_ELIGIBLE
MK2 build = GATED
```