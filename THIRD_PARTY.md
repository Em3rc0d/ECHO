# Third-party Registry — research-stage

Este archivo separa la licencia de ECHO de la licencia de cada dependencia, checkpoint y dataset.

## Software / standards candidates

| Component | Role | Audit finding | Policy |
|---|---|---|---|
| TensorFlow / YAMNet code | baseline model stack | Apache-2.0 en TensorFlow Model Garden/source family | pin exact version before distribution |
| PANNs repository | challenger | MIT source repository | verify exact checkpoint provenance separately |
| HTS-AT repository | extended | MIT source repository | MK2/deferred |
| PaSST repository | extended | Apache-2.0 source repository | MK2/deferred |
| BEATs source | extended | MIT source repository | verify exact checkpoint before distribution |
| FFmpeg | RTSP decode/normalization | LGPL 2.1+ by default; build options can introduce GPL obligations | prefer system/external binary initially; record exact build/config |
| GStreamer | streaming fallback | core/plugins commonly LGPL; plugin dependency licenses vary | pin exact plugins if packaged |
| go2rtc | optional relay | MIT project | optional, not core MK1 dependency |
| Eclipse Mosquitto | MQTT broker | project site identifies open-source EPL/EDL licensing | prefer external service/package; pin version |
| MQTT 5.0 | protocol | OASIS standard | specification, not an ECHO code dependency |

## Dataset/license policy

| Dataset | Policy |
|---|---|
| AudioSet | use metadata/ontology/reference according to stated licenses; do not infer redistribution rights for underlying YouTube media |
| FSD50K | inspect **each clip license**; asset registry must block incompatible use |
| ESC-50 | full dataset is research/non-commercial constrained; do not silently use as unrestricted production corpus |
| SONYC-UST | pin release and its stated license/terms in dataset manifest |
| DCASE datasets | verify each task/release independently |

## Mandatory before a distributable ECHO release

1. choose ECHO-owned source license explicitly;
2. lock dependency versions;
3. record repository/package/checkpoint license for exact artifacts;
4. generate notices/attributions;
5. ensure no restricted dataset/audio is bundled or redistributed incorrectly;
6. record FFmpeg/GStreamer binary/build licensing if shipped.

**Status:** registry certified as a governance mechanism. Exact release bill-of-materials remains a build artifact.