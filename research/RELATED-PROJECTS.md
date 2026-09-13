# Related Projects / Ecosystem

| Proyecto | Qué ya resuelve | Qué aprende ECHO | Qué NO copiar |
|---|---|---|---|
| Frigate | IP cameras, FFmpeg, audio detection, events, MQTT, restream | source roles, volume gating, event lifecycle, MQTT patterns | convertir ECHO en NVR/video platform |
| Frigate MQTT | topics/event states | desacoplar detection de consumers | schema exacto del producto |
| go2rtc | relay/restream multiprotocolo | reducir conexiones a cámaras y fan-out | hard dependency en PoC |
| Crywatch | RTSP -> go2rtc -> FFmpeg -> YAMNet -> temporal decisions -> alerts | streaming + sustained positives + cooldown | thresholds/caso baby monitor |
| Real-Time-Sound-Event-Detection | YAMNet live inference | referencia de loop realtime | asumir que demo = producción |
| PANNs repo | pretrained audio models / frame-wise variants | challenger/model research | stack completo como dependencia obligatoria |
| SONYC baseline | multilabel urban sensor inference | evaluación realista en red de sensores | taxonomía urbana como taxonomía ECHO |
| MIMII baseline | industrial anomaly sound | domain robustness ideas | confundir anomaly detection con event classification |

## Valor propio de ECHO

Gran parte del plumbing ya existe. ECHO aporta integración disciplinada alrededor de:

```text
multi-source acoustic ingestion
+ domain-specific transfer/benchmarking
+ temporal event engine
+ versioned contracts
+ operational Pub/Sub
+ field robustness
+ reproducible evidence/provenance
```

La innovación de ingeniería no debe venderse como “inventamos YAMNet/RTSP/MQTT”, sino como un sistema cohesivo, auditable y evaluado para convertir audio ambiental en eventos acústicos confiables.

## Fuentes

- Frigate audio: https://docs.frigate.video/configuration/audio_detectors/
- Frigate MQTT: https://docs.frigate.video/integrations/mqtt/
- Frigate restream: https://docs.frigate.video/configuration/restream
- go2rtc: https://github.com/AlexxIT/go2rtc
- Crywatch: https://github.com/drjc1001/crywatch
- Real-Time-Sound-Event-Detection: https://github.com/robertanto/Real-Time-Sound-Event-Detection
- PANNs: https://github.com/qiuqiangkong/audioset_tagging_cnn
- SONYC baseline: https://github.com/sonyc-project/urban-sound-tagging-baseline
- MIMII baseline: https://github.com/MIMII-hitachi/mimii_baseline