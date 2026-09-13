# Quarry — Models

**Status:** `CERTIFIED_FOR_BENCHMARK_SCOPE`  
**Winner:** `EMPIRICAL / MK1`

## 1. Purpose

This quarry determines which model families deserve a controlled ECHO benchmark and what evidence is required before one becomes the production candidate. It explicitly prevents the project from choosing a model because it is fashionable or because a paper reports a high score on a different dataset.

## 2. Operational constraints

ECHO is a continuous acoustic-event system, so model quality is only one axis. Every candidate must be evaluated against:

```text
per-class recall/precision
macro/micro F1
false alarms per source-hour
streaming detection latency
CPU/GPU utilization
RAM/VRAM
artifact size
throughput under N sources
calibration
export/runtime stability
license and maintenance risk
```

## 3. Baseline/challenger set

| ID | Family | ECHO role | Strength | Main risk |
|---|---|---|---|---|
| A | YAMNet + ECHO head | mandatory baseline | compact pretrained AudioSet representation; official transfer-learning path | domain shift; TensorFlow/runtime pinning |
| B | PANNs/Cnn14 + ECHO head | mandatory challenger | strong AudioSet representation; established audio-tagging ecosystem | larger footprint and integration complexity |
| C | compact ECHO log-mel CNN | mandatory control | full control, simple deployment, no pretrained backbone assumption | may require more labeled data |
| D | AST | extended challenger | transformer global context | latency/footprint |
| E | HTS-AT | extended challenger | hierarchical transformer suitable for audio tagging/detection research | complexity and compute |
| F | PaSST | extended challenger | Patchout reduces transformer cost | deployment/export evidence needed |
| G | BEATs/ATST-class SSL | extended representation challenger | strong modern pretrained features | model size, runtime and checkpoint/license complexity |

## 4. YAMNet facts relevant to ECHO

`FACT/EVIDENCE`: TensorFlow's official transfer-learning tutorial describes YAMNet as MobileNetV1-based, consuming mono 16 kHz waveform, producing independent AudioSet class scores, log-mel representation and 1024-dimensional embeddings. The documented framing uses roughly 0.96 s frames with a 0.48 s hop.

ECHO implication: YAMNet is a good **feature baseline**, but its 521 labels are not the ECHO taxonomy. ECHO must train its own head and calibrate its own event logic.

Source: https://www.tensorflow.org/tutorials/audio/transfer_learning_audio

## 5. PANNs/Cnn14 role

PANNs is retained because it provides a materially different pretrained CNN representation from YAMNet and has established AudioSet training. It should be evaluated both as frozen feature extractor and, if resources/data justify it, with controlled fine-tuning.

Source: https://arxiv.org/abs/1912.10211 and original repository referenced in `research/MODEL-MATRIX.md`.

## 6. Why a custom CNN remains mandatory

The custom compact CNN is not a fallback of last resort. It is the scientific control that answers:

> Are pretrained embeddings actually buying ECHO enough robustness to justify their complexity?

If a small model achieves comparable field false-alarm and recall behavior at much lower resource cost, that is a legitimate winner.

## 7. Training regimes

Each backbone may have different regimes, but comparisons must label them clearly:

```text
frozen representation
partial fine-tuning
full fine-tuning
from scratch
```

Do not compare “YAMNet frozen” against “PANNs fully fine-tuned” and attribute all difference to architecture without noting training regime.

## 8. Streaming suitability

A model is not approved by clip inference alone. Benchmark must measure:

- window preprocessing cost;
- inference p50/p95/p99;
- model warm-up;
- batch=1 latency;
- optional multi-source batching throughput;
- memory stability over long replay;
- ability to preserve source ordering/identity.

## 9. Export/runtime matrix

For each finalist record:

```text
training framework
runtime framework
CPU support
GPU support
ONNX feasibility
TFLite feasibility when relevant
quantization feasibility
unsupported ops
artifact size
runtime version
```

Export is not a requirement for MK1 if native runtime is stable, but portability becomes an MK2 decision.

## 10. Calibration and scores

Raw neural scores are not assumed to be probabilities. Validation must determine whether post-hoc calibration improves reliability. Thresholds are per-class candidates because score distributions can differ substantially across targets.

## 11. Model-selection logic

No single weighted leaderboard score is certified. Selection follows constraints + Pareto:

1. remove candidates that cannot satisfy operational limits;
2. compare remaining models on critical recall, false alarms, macro F1, latency and resources;
3. inspect error families manually;
4. prefer simpler model when quality is statistically/operationally equivalent.

## 12. Failure modes

- public-dataset overfitting;
- weak-label noise;
- catastrophic degradation on camera codecs;
- overconfidence on OOD audio;
- high false alarms on long negative streams;
- CPU saturation under multi-source load;
- fine-tuning instability with small field corpus;
- dependency/checkpoint license incompatibility.

## 13. Closed decisions

- A/B/C are mandatory benchmark arms.
- D/G families are optional challengers, not blockers.
- no model winner is chosen before ECHO-domain evidence.
- model artifact includes preprocessing, labels, calibrator and thresholds/version metadata.

## 14. Invalidation conditions

Re-open benchmark scope if the MK1 taxonomy changes substantially, if a candidate's license/runtime becomes unusable, or if A/B/C all fail the operational envelope.

## 15. Downstream outputs

This quarry feeds `MK0/plan/BENCHMARK-DESIGN.md`, `MK1/plan/BENCHMARK-PROTOCOL.md`, model packaging and MK2 model governance.
