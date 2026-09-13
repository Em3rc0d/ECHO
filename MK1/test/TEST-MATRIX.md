# Test Matrix — MK1

| Layer | Tests |
|---|---|
| domain/contracts | schema validation, timestamp/order invariants |
| audio | resample, downmix, clipping, gaps, exact window boundaries |
| model adapter | deterministic fixture, shape/errors, version metadata |
| event engine | thresholds, hysteresis, merge, cooldown, simultaneous classes |
| source | file EOF, RTSP auth/no-audio/disconnect/reconnect |
| MQTT | publish, broker unavailable, QoS1 duplicate handling |
| E2E | file -> event -> subscriber; camera -> event si gate abierto |
| performance | latency, RTF, memory, N replay sources |
| privacy | no secret/audio leakage in logs/events |

Cada test que cierra un gate debe generar resultado machine-readable.