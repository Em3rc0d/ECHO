# Model Landscape — audited

**Audit:** 2026-09-13

## Selection rule

Un benchmark publicado en otro corpus no selecciona el modelo ECHO. El ganador se decide con el protocolo propio y target/runtime constraints.

| Modelo | Arquitectura/pretraining | Rol | Estado MK1 | Riesgo principal |
|---|---|---|---|---|
| YAMNet | MobileNetV1, AudioSet | Baseline A / embeddings | CERTIFIED_FOR_BENCHMARK | domain shift / TensorFlow runtime |
| PANNs Cnn14 | CNN, AudioSet | Challenger B | CERTIFIED_FOR_BENCHMARK | footprint/latency mayor |
| ECHO custom log-mel CNN | CNN propia | Control C | CERTIFIED_FOR_BENCHMARK | menos prior; necesita suficiente data |
| AST | audio spectrogram transformer | extended challenger | DEFERRED_MK2 | compute/latency/export |
| HTS-AT | hierarchical token-semantic transformer | extended challenger | DEFERRED_MK2 | complexity/compute |
| PaSST | patchout spectrogram transformer | extended challenger | DEFERRED_MK2 | integration/runtime |
| BEATs | self-supervised audio representation | representation challenger | DEFERRED_MK2 | deployment footprint/complexity |

## YAMNet certified facts

Fuente: https://www.tensorflow.org/tutorials/audio/transfer_learning_audio

- MobileNetV1 depthwise-separable architecture;
- 521 AudioSet event outputs;
- input mono 16 kHz float waveform;
- frames de 0.96 s;
- hop de 0.48 s;
- outputs: scores, log-mel spectrogram, embeddings;
- embedding = 1024 dimensiones;
- TensorFlow documenta explícitamente transfer learning sobre embeddings.

Por eso YAMNet es el baseline inicial más defendible para ECHO, **no** porque esté predeclarado ganador.

## PANNs

PANNs se conserva como challenger porque el trabajo/repo original ofrece AudioSet-pretrained CNNs y variantes para tagging/SED. MK1 debe medir la variante/weight exacta, su preprocessing y runtime bajo el mismo corpus que A/C.

## Extended models

AST, HTS-AT, PaSST y BEATs quedan investigados/certificados como candidatos conocidos pero **deferred**. No existe razón para ampliar el search space de MK1 antes de que A/B/C establezca una base empírica. Pueden entrar si:

1. A/B/C no cumple constraints;
2. MK2 necesita mejor tradeoff;
3. existe hardware suficiente;
4. licencia/checkpoint/export están verificados para la versión exacta.

## Required run manifest

Todo modelo ejecutado debe registrar:

```text
model_family
source/repository
source_version/commit
checkpoint_id + sha256
checkpoint_license/provenance
preprocessing version
sample_rate
window/hop
feature config
head architecture
training config hash
dataset manifest hash
runtime/library versions
hardware
```

## Metrics

```text
per-class precision/recall/F1/PR-AUC
macro/micro F1
false alarms/source-hour
misses/class
detection latency p50/p95/p99
CPU/RAM/model size/throughput
calibration
PSDS when strong temporal labels support it
```

## Primary sources

- YAMNet/TensorFlow: https://www.tensorflow.org/tutorials/audio/transfer_learning_audio
- PANNs paper: https://arxiv.org/abs/1912.10211
- PANNs repo: https://github.com/qiuqiangkong/audioset_tagging_cnn
- AST repo: https://github.com/YuanGongND/ast
- HTS-AT repo: https://github.com/RetroCirce/HTS-Audio-Transformer
- PaSST repo: https://github.com/kkoutini/PaSST
- BEATs source: https://github.com/microsoft/unilm/tree/master/beats