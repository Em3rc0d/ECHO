# Risk Register / FMEA

**Status:** `ACTIVE / REVIEW_EACH_TEST_GATE`  
**Purpose:** track technical, scientific, operational, privacy, security and supply-chain failure modes that can invalidate ECHO claims.

## 1. Method

The register uses qualitative probability (`L/M/H`) and impact (`L/M/H/Critical`) during pre-build design. Once MK1/MK2 produce empirical evidence, high-priority risks should add measurable occurrence/detection data instead of retaining purely qualitative labels.

A risk is not closed because a mitigation is written down. It is closed or reduced only when a control is implemented/tested and evidence is linked.

## 2. Core FMEA register

| ID | Failure mode | P | I | Observable effect | Preventive/control strategy | Evidence required |
|---|---|---:|---:|---|---|---|
| R-01 | camera microphone poor/noisy | H | H | low recall, unstable scores | field/device benchmark; mic fallback | device comparison + SNR/error analysis |
| R-02 | camera exposes no audio | M | H | no ingest | external mic/NVR source abstraction | hardware probe |
| R-03 | AGC/codec damages transients | M | H | glass/shatter misses | codec/AGC ablation | replay/field matrix |
| R-04 | RTSP jitter/packet loss | M | H | gaps, stale windows | bounded buffering + telemetry + reconnect | network fault tests |
| R-05 | public-data domain shift | H | Critical | misleading offline quality | field holdout + device/site stratification | field benchmark |
| R-06 | hard-negative false alarms | H | Critical | alert fatigue/unusable system | hard-negative mining + thresholds + Event Engine | false alarms/source-hour |
| R-07 | critical event missed | M | Critical | false negative | recall-first analysis + SNR/distance testing | per-class misses/recall |
| R-08 | dataset leakage | M | Critical | scientifically invalid benchmark | group-aware splits + duplicate audit | split audit |
| R-09 | ambiguous/mislabeled audio | H | H | performance ceiling/noisy evaluation | annotation guide + adjudication | sample audit/inter-annotator notes |
| R-10 | overlapping events | H | H | mutually-exclusive classifier fails | multi-label contract | polyphonic test set |
| R-11 | one global threshold | H | H | class-specific precision/recall failure | validation-derived per-class thresholds | PR curves/calibration |
| R-12 | unbounded queue/buffer | M | Critical | RAM growth + stale alarms | bounded queues + overload policy | load/soak evidence |
| R-13 | reconnect storm | M | H | service contention | exponential backoff + jitter | fault injection |
| R-14 | MQTT broker outage | M | H | event delivery interruption | detector/broker isolation; MK2 outbox/durability policy if required | broker outage test |
| R-15 | QoS1 duplicate | H | M | duplicate events/actions | `event_id` idempotency | duplicate delivery test |
| R-16 | replay from loudspeaker | M | H | event is acoustically real but source is spoofed | document boundary; anti-spoof research if required | threat test only if in scope |
| R-17 | clock drift | M | M | bad timestamps/correlation | UTC/NTP/session sequence | timing audit |
| R-18 | model/data drift | M | H | performance degrades after release | regression replay + field monitoring | version-to-version benchmark |
| R-19 | incompatible data/checkpoint license | M | H | release blocked | asset/checkpoint manifest | license audit |
| R-20 | credentials committed/logged | M | Critical | camera/network compromise | external secrets + redaction + scanning | repo/log scan |
| R-21 | unnecessary conversation retention | M | H | privacy exposure | ephemeral buffers, retention off | filesystem/temp/log audit |
| R-22 | hardware insufficient | M | H | queue lag/drops | capacity profiling | N-source load/soak |
| R-23 | runtime/model dependency drift | M | M | irreproducible build | pin/hash runtime/model | reproducibility test |
| R-24 | aggregate accuracy hides class failure | H | H | unsafe selection | per-class + macro + operational metrics | benchmark report |
| R-25 | unmeasured distance claim | H | H | false requirement/expectation | distance/SNR protocol | field test |
| R-26 | source state leaks across cameras | M | Critical | wrong camera/event association | state keyed by source+event | concurrent replay test |
| R-27 | stale inference emitted after reconnect | M | H | wrong temporal event | stream_generation + sequence validation | reconnect race test |
| R-28 | model score poorly calibrated | M | H | thresholds brittle | calibration/reliability analysis | Brier/reliability/ECE |
| R-29 | long negative audio not represented | H | Critical | demo passes, always-on mode fails | continuous negative replay | source-hours negative evidence |
| R-30 | deployment config/schema mismatch | M | H | runtime errors/wrong semantics | versioned config/schema validation | startup/compat tests |
| R-31 | checkpoint supply-chain substitution | L/M | H | unexpected model/artifact | hash + official provenance | checksum/manifest |
| R-32 | one noisy source starves others | M | H | unfair multi-source latency | per-source bounded queue + fair scheduling | adversarial load test |
| R-33 | logging high-cardinality/raw media | M | M/H | resource/privacy issue | telemetry schema + sampling/redaction | observability review |
| R-34 | test set used for tuning | M | Critical | optimistic metrics | frozen test governance | run history audit |
| R-35 | field holdout contaminates training | M | Critical | invalid domain claim | manifest permissions/split immutability | manifest diff audit |

## 3. Risk clusters

Scientific validity risks such as domain shift, leakage, label ambiguity, aggregate-only metrics, poor calibration and test contamination can create a convincing demo with invalid conclusions. Continuous-operation risks determine whether the system remains useful outside short clips. Security/privacy risks require controls independent of classifier quality.

## 4. Review cadence

Review at end of MK0 test, before MK1 build, after the first benchmark, after streaming E2E, after camera integration, before MK1 certification, during MK2 capacity/security design and before release.

## 5. Escalation rule

Any new `Critical` risk that can invalidate architecture or scientific evidence blocks the dependent gate until mitigated, converted into a controlled experiment, or explicitly accepted with rationale.

## 6. Evidence format

```yaml
risk_id: R-xx
control_version: ...
test_or_evidence: path/uri
result: PASS|FAIL|PARTIAL
measured_at: ...
commit/config/model: ...
residual_risk: ...
owner_or_gate: ...
```

## 7. Invalidation

Model, taxonomy, deployment, source hardware, data policy, broker semantics or privacy changes may introduce new risks or increase previously reduced ones. The register is versioned and never treated as a one-time checklist.