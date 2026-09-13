# Source Catalog

Provenance labels usadas en MK0:

- `FACT/EVIDENCE`: afirmación directamente soportada por fuente.
- `INFERENCE`: conclusión de ingeniería derivada de evidencia.
- `HYPOTHESIS`: debe probarse.
- `DECISION_CANDIDATE`: opción propuesta aún no cerrada.

| ID | Área | Fuente | Tipo | Nota |
|---|---|---|---|---|
| S-001 | AudioSet | https://research.google.com/audioset/ | primary | ontology + dataset metadata |
| S-002 | YAMNet | https://www.tensorflow.org/tutorials/audio/transfer_learning_audio | primary | official transfer-learning flow |
| S-003 | YAMNet code | https://github.com/tensorflow/models/tree/master/research/audioset/yamnet | primary | implementation/spec |
| S-004 | PANNs paper | https://arxiv.org/abs/1912.10211 | paper | pretrained audio networks |
| S-005 | PANNs repo | https://github.com/qiuqiangkong/audioset_tagging_cnn | primary code | models/checkpoints/license |
| S-006 | AST | https://arxiv.org/abs/2104.01778 | paper | audio transformer |
| S-007 | AST code | https://github.com/YuanGongND/ast | primary code | official implementation |
| S-008 | HTS-AT | https://github.com/RetroCirce/HTS-Audio-Transformer | primary code | hierarchical transformer |
| S-009 | Frigate audio | https://docs.frigate.video/configuration/audio_detectors/ | primary docs | production pattern |
| S-010 | Frigate MQTT | https://docs.frigate.video/integrations/mqtt/ | primary docs | pub/sub pattern |
| S-011 | go2rtc | https://github.com/AlexxIT/go2rtc | primary code | stream relay |
| S-012 | ONVIF | https://www.onvif.org/ | standards body | IP security interoperability |
| S-013 | FFmpeg RTSP | https://ffmpeg.org/ffmpeg-protocols.html | primary docs | ingestion/transport |
| S-014 | MQTT | https://mqtt.org/mqtt-specification/ | standard | Pub/Sub semantics |
| S-015 | Mosquitto | https://mosquitto.org/ | primary | open-source broker |
| S-016 | FSD50K | https://zenodo.org/records/4060432 | dataset release | open sound data |
| S-017 | ESC-50 | https://github.com/karolpiczak/ESC-50 | dataset release | benchmark |
| S-018 | UrbanSound8K | https://zenodo.org/records/1203745 | dataset release | urban benchmark |
| S-019 | SONYC-UST | https://zenodo.org/records/3966543 | dataset release | sensor network/multilabel |
| S-020 | MIMII | https://zenodo.org/records/3384388 | dataset release | industrial noise/domain |
| S-021 | DCASE | https://dcase.community/ | challenge | SED methodology |
| S-022 | in-toto | https://in-toto.io/ | primary docs | attestation chain |
| S-023 | Sigstore/Cosign | https://docs.sigstore.dev/ | primary docs | artifact signing |
| S-024 | SLSA | https://slsa.dev/ | standard | provenance framework |

Este catálogo es vivo. Agregar una fuente no implica aprobar una dependencia.