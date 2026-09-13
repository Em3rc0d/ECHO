# MK0 Evidence Ledger

**Status:** `CERTIFIED_SNAPSHOT / EXTENDABLE`

## Purpose

Provide traceable evidence nodes that support MK0 decisions. This ledger is intentionally separate from the decision log: evidence can be true while ECHO chooses a different engineering option.

## Core evidence nodes

| ID | Domain | Source | Claim supported | ECHO implication |
|---|---|---|---|---|
| EV-AI-001 | model | TensorFlow YAMNet transfer-learning docs | YAMNet waveform/embedding transfer-learning path | baseline A feasible |
| EV-AI-002 | model | PANNs paper/repo | AudioSet-pretrained CNN family and embeddings | challenger B feasible |
| EV-AI-003 | model | AST paper/repo | transformer audio classification path | extended candidate |
| EV-AI-004 | model | HTS-AT repo/paper | hierarchical transformer path | extended/MK2 candidate |
| EV-AI-005 | model | PaSST paper/repo | patchout transformer efficiency approach | extended candidate |
| EV-AI-006 | model | BEATs paper/repo | self-supervised/general audio representation | representation challenger |
| EV-DATA-001 | dataset | AudioSet official site | large human-labeled ontology/media metadata | pretraining/ontology reference |
| EV-DATA-002 | dataset | FSD50K Zenodo | 51k+ clips, multilabel, per-clip licensing | filtered corpus source |
| EV-DATA-003 | dataset | SONYC-UST release | real urban sensor/multilabel data | domain/polyphony evidence |
| EV-DATA-004 | dataset | ESC-50 official repo | small balanced environmental benchmark | sanity benchmark only |
| EV-DATA-005 | dataset | UrbanSound8K official release/site | urban event benchmark | domain contrast |
| EV-DATA-006 | dataset | DCASE/DESED | temporal/polyphonic SED tasks/metrics | evaluation methodology |
| EV-STREAM-001 | ingest | ONVIF Profile T | interoperable media/profile concepts including audio where implemented | discovery/profile evidence |
| EV-STREAM-002 | ingest | FFmpeg docs | RTSP transport/decoding support | decoder baseline |
| EV-STREAM-003 | ingest | GStreamer rtspsrc docs | configurable RTSP/jitter handling | fallback evidence |
| EV-BUS-001 | messaging | MQTT 5.0 OASIS | QoS semantics including at-least-once QoS1 | idempotency requirement |
| EV-BUS-002 | messaging | Eclipse Mosquitto | lightweight open-source MQTT broker | MK1 broker candidate |
| EV-SYS-001 | related | Frigate docs | camera-scoped audio detection + MQTT patterns | operational precedent |
| EV-PRIV-001 | privacy | Peru ANPD normative sources | personal-data/videovigilance framework context | field compliance gate |

## Evidence quality

Evidence supports only the exact claim captured. Example: ONVIF Profile T support in a standard does not prove the professor's camera implements it. That remains `EXT-CAMERA-001`.

## License/provenance rule

Model code license, checkpoint license, dataset release terms and individual clip license are recorded independently. A release landing page is not enough when assets have mixed licenses.

## Expansion policy

New evidence receives a stable ID and is appended. Existing IDs are not repurposed. If a source is corrected or superseded, record a successor and impact review.

## Downstream consumers

Quarries, research matrices, decision log and certification ledger cite these nodes conceptually and by source path/URL.

## Invalidation

A stale source does not automatically invalidate a decision if equivalent evidence remains, but dependency review is required for material claims.