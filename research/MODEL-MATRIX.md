# ECHO Model Landscape and Decision Matrix

**Status:** `MK0_CERTIFIED_LANDSCAPE / MK1_WINNER_PENDING`

## 1. Purpose

Compare model families relevant to ECHO before any winner is selected. Published benchmark scores are contextual evidence only; ECHO selects a model on its own taxonomy, data, continuous replay and hardware.

## 2. Evaluation dimensions

Representation quality; transfer-learning path; input/frontend requirements; model/checkpoint licensing; model size; CPU/GPU inference; memory; export/deployment options; maintenance/ecosystem; multi-label suitability; temporal/stream integration; calibration behavior and ease of reproducing a frozen artifact.

## 3. Candidate matrix

| Candidate | Family | Pretraining | MK1 role | Expected strength | Main risk | Decision |
|---|---|---|---|---|---|---|
| YAMNet | MobileNetV1 CNN | AudioSet | A baseline | compact embeddings, official TF transfer-learning path | domain shift/runtime pinning | benchmark |
| PANNs Cnn14 | CNN | AudioSet | B challenger | strong general acoustic representation | larger footprint | benchmark |
| ECHO compact CNN | log-mel CNN | none | C control | simple deployment, full control | needs more task data | benchmark |
| AST | spectrogram transformer | AudioSet/ImageNet recipes | extended | strong global attention/audio tagging history | compute/latency | defer/extend |
| HTS-AT | hierarchical transformer | AudioSet recipes | extended/MK2 | classification/detection-oriented hierarchy | implementation complexity | defer |
| PaSST | patchout transformer | AudioSet | extended/MK2 | transformer with efficiency strategy | runtime/export to measure | defer |
| BEATs | self-supervised transformer | large audio pretraining | representation challenger | modern general embeddings | footprint/deployment/checkpoint governance | defer |

## 4. YAMNet evidence

Official TensorFlow transfer-learning documentation describes a YAMNet path using mono 16 kHz waveform and exposes class scores and a 1024-dimensional embedding. The referenced implementation processes overlapping short frames. ECHO uses the embedding/backbone rather than adopting AudioSet's label set as product taxonomy.

### ECHO experiments

A1 frozen embeddings + linear/small MLP. A2 frozen embeddings + tuned head. A3 partial fine-tuning only if A1/A2 plateau and data/runtime justify it.

## 5. PANNs/Cnn14 evidence

The PANNs paper/repository describes AudioSet-pretrained CNN architectures including Cnn14 and transfer representations. ECHO measures feature extraction/fine-tuning separately because quality gains may have material memory/latency consequences.

## 6. Custom CNN control

A compact log-mel model trained directly on ECHO labels establishes whether large pretraining materially improves the narrow problem. It also provides a lower-complexity deployment baseline and protects the study from assuming that “newer/larger = better”.

## 7. Transformer/SSL challengers

AST, HTS-AT, PaSST and BEATs are scientifically relevant but not mandatory before A/B/C evidence. Each requires exact preprocessing, checkpoint/license and runtime evaluation. They are promoted if the first frontier fails or MK2 research justifies extra compute.

## 8. Common benchmark protocol

Same admitted data/groups, taxonomy, field/test isolation, threshold-calibration policy and declared hardware. Record code/checkpoint/config/manifest hashes. Batch=1 latency is mandatory; multi-source batching is an additional experiment.

## 9. Metrics

Per-class precision/recall/F1/PR-AUC, macro/micro summaries, calibration, false alarms/source-hour, misses/event recall, latency p50/p95/p99, throughput, CPU/GPU/RAM/VRAM, artifact size and capacity impact.

## 10. Selection rule

First eliminate scientifically invalid or operationally infeasible candidates. Then select from the Pareto frontier rather than using an arbitrary weighted score. Error analysis is required before declaring `EMP-MODEL-001` closed.

## 11. Licensing/provenance

Code-repository license and checkpoint license are separate. Exact selected artifacts enter `THIRD_PARTY.md`/model manifest with hash and permitted use before release.

## 12. Invalidation

A taxonomy/data/frontend change invalidates affected benchmark comparability. New model families can be appended without rewriting historical evidence.

## Primary references

- TensorFlow YAMNet transfer learning: https://www.tensorflow.org/tutorials/audio/transfer_learning_audio
- YAMNet source family: https://github.com/tensorflow/models/tree/master/research/audioset/yamnet
- PANNs: https://arxiv.org/abs/1912.10211 and https://github.com/qiuqiangkong/audioset_tagging_cnn
- AST: https://arxiv.org/abs/2104.01778 and https://github.com/YuanGongND/ast
- HTS-AT: https://github.com/RetroCirce/HTS-Audio-Transformer
- PaSST and BEATs exact artifacts/licenses must be pinned when promoted.