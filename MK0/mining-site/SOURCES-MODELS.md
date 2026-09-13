# Sources — Models

Consulta base: 2026-09.

| Fuente | Evidencia útil | URL |
|---|---|---|
| TensorFlow YAMNet transfer learning | 521 clases; MobileNetV1; mono 16 kHz; frames 0.96 s / hop 0.48 s; embeddings 1024D | https://www.tensorflow.org/tutorials/audio/transfer_learning_audio |
| TensorFlow Hub YAMNet | inferencia/clases AudioSet | https://www.tensorflow.org/hub/tutorials/yamnet |
| PANNs paper | pretraining AudioSet; CNNs; transferencia | https://arxiv.org/abs/1912.10211 |
| PANNs official repo | checkpoints, tagging/SED, MIT code | https://github.com/qiuqiangkong/audioset_tagging_cnn |
| AST | transformer puro para spectrogram | https://arxiv.org/abs/2104.01778 |
| HTS-AT | transformer jerárquico; clasificación + localización | https://arxiv.org/abs/2202.00874 |
| BEATs | self-supervised audio pretraining con acoustic tokenizers | https://arxiv.org/abs/2212.09058 |
| BEATs official implementation | checkpoints/evaluación | https://github.com/microsoft/unilm/tree/master/beats |
| CLAP | audio-text contrastive / zero-shot | https://arxiv.org/abs/2206.04769 |

## Lectura ECHO

YAMNet y PANNs son candidatos prácticos para MK1 por madurez y facilidad de transferencia. AST/HTS-AT/BEATs/CLAP son challengers de investigación; una cifra SOTA externa no prueba conveniencia operacional en cámara CPU/edge.