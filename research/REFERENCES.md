# ECHO References

**Status:** `CURATED_PRIMARY_REFERENCE_INDEX`

## Models / representation learning

- TensorFlow — Transfer learning with YAMNet: https://www.tensorflow.org/tutorials/audio/transfer_learning_audio
- TensorFlow Models — YAMNet source: https://github.com/tensorflow/models/tree/master/research/audioset/yamnet
- Kong et al. — PANNs: Large-Scale Pretrained Audio Neural Networks for Audio Pattern Recognition: https://arxiv.org/abs/1912.10211
- PANNs author repository: https://github.com/qiuqiangkong/audioset_tagging_cnn
- Gong et al. — AST: Audio Spectrogram Transformer: https://arxiv.org/abs/2104.01778
- AST repository: https://github.com/YuanGongND/ast
- HTS-AT repository: https://github.com/RetroCirce/HTS-Audio-Transformer

PaSST/BEATs references should be pinned to the exact paper/repository/checkpoint version if they enter an ECHO benchmark/release.

## Datasets / sound-event evaluation

- AudioSet: https://research.google.com/audioset/
- FSD50K official Zenodo release: https://zenodo.org/records/4060432
- ESC-50: https://github.com/karolpiczak/ESC-50
- UrbanSound8K: https://urbansounddataset.weebly.com/urbansound8k.html
- SONYC-UST: https://zenodo.org/records/3966543
- DCASE community/challenges: https://dcase.community/
- DCASE 2024 Task 4 SED reference: https://dcase.community/challenge2024/task-sound-event-detection-with-heterogeneous-training-dataset-and-potentially-missing-labels

## Streaming / camera integration

- ONVIF Profile T: https://www.onvif.org/profiles/profile-t/
- FFmpeg protocols/RTSP: https://ffmpeg.org/ffmpeg-protocols.html
- GStreamer RTSP source documentation: https://gstreamer.freedesktop.org/documentation/rtsp/rtspsrc.html

Exact manufacturer/NVR documentation is added after `EXT-CAMERA-001` resolves the device.

## Messaging / related systems

- OASIS MQTT 5.0: https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html
- Eclipse Mosquitto: https://mosquitto.org/
- Frigate audio detection: https://docs.frigate.video/configuration/audio_detectors/
- Frigate MQTT integration: https://docs.frigate.video/integrations/mqtt/

## Privacy / governance

- Peru ANPD official portal and normative publications: https://www.gob.pe/institucion/anpd

Exact legal references are tracked in `governance/PRIVACY-COMPLIANCE.md`; this project documentation is not legal advice.

## Reference usage policy

Prefer these canonical primary sources in engineering artifacts. When a claim depends on a release/license, cite the exact release/version rather than only this index. External papers/results provide context; they do not certify ECHO performance.