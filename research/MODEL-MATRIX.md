# Model Landscape

## Regla

No se selecciona ganador por benchmark publicado en otro dataset. ECHO selecciona por su propio Pareto: recall crítico, macro F1, falsas alarmas, latencia, memoria/CPU y facilidad operativa.

| Modelo | Tipo | Pretraining | Papel ECHO | Fortalezas | Riesgos | Estado |
|---|---|---|---|---|---|---|
| YAMNet | MobileNetV1 CNN | AudioSet | Baseline A | compacto, 16 kHz, embeddings 1024, TF transfer-learning oficial | domain shift; runtime/version pinning | BENCHMARK_REQUIRED |
| PANNs/Cnn14 | CNN | AudioSet | Challenger B | representaciones fuertes; embeddings; SED variants | footprint mayor | BENCHMARK_REQUIRED |
| ECHO CNN log-mel | CNN propia | ninguno | Control C | control total, deployment simple | requiere más data; menor prior | BENCHMARK_REQUIRED |
| AST | pure transformer | Audio/ImageNet-AudioSet recipes | Challenger extendido | contexto global; buen historial de audio tagging | coste/latencia/footprint | MK1_EXTENDED_OR_MK2 |
| HTS-AT | hierarchical audio transformer | AudioSet recipes | Challenger extendido | clasificación + detection orientation | complejidad/compute | MK2_CANDIDATE |
| PaSST | patchout spectrogram transformer | AudioSet | Challenger extendido | eficiencia vs transformers clásicos | integration/footprint a medir | MK2_CANDIDATE |
| BEATs | self-supervised audio transformer | large audio pretraining | Representation challenger | embeddings generales modernos | mayor complejidad y deployment | MK2_CANDIDATE |

## YAMNet facts útiles

- entrada: waveform mono 16 kHz;
- patch aproximado: 0.96 s;
- hop aproximado: 0.48 s;
- output: class scores + log-mel + embedding de 1024 dimensiones;
- clases del modelo publicado: 521 AudioSet classes;
- uso recomendado en ECHO: extractor/backbone, no taxonomía final del producto.

## PANNs

Cnn14 sirve como challenger porque fue preentrenado en AudioSet y el ecosistema oficial incluye modelos con salidas de tagging y variantes de frame-wise detection. El benchmark de ECHO debe medir inferencia CPU, memoria, latencia y calidad de embeddings sobre exactamente los mismos splits.

## Transformers

AST, HTS-AT, PaSST y BEATs se mantienen como candidatos de investigación, no como default inicial. Para cada uno MK0/MK1 debe verificar por separado:

- licencia del código;
- licencia del checkpoint;
- requisitos de preprocessing;
- sample rate/input duration;
- export/ONNX/TFLite si aplica;
- latencia CPU;
- tamaño de modelo;
- batch behavior;
- mantenimiento del repo.

## Benchmark protocol

Mismos:

- clips y splits;
- augmentations;
- labels;
- threshold calibration protocol;
- hardware;
- warm-up;
- batch policy;
- métricas.

Reportar:

```text
Precision/Recall/F1 por clase
Macro/Micro F1
PR-AUC
False alarms/hour (stream replay)
Latency p50/p95/p99
CPU/RAM
model size
throughput windows/s
calibration
```

### Fuentes primarias

- YAMNet/TensorFlow: https://www.tensorflow.org/tutorials/audio/transfer_learning_audio
- YAMNet repo: https://github.com/tensorflow/models/tree/master/research/audioset/yamnet
- PANNs paper: https://arxiv.org/abs/1912.10211
- PANNs repo: https://github.com/qiuqiangkong/audioset_tagging_cnn
- AST paper: https://arxiv.org/abs/2104.01778
- AST repo: https://github.com/YuanGongND/ast
- HTS-AT repo: https://github.com/RetroCirce/HTS-Audio-Transformer

Licencias de checkpoints y cualquier asset se verifican individualmente antes de integración.