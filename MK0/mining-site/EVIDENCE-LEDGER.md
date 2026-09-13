# MK0 Evidence Ledger

| ID | Claim | Tipo | Fuente | Consecuencia ECHO |
|---|---|---|---|---|
| EV-001 | YAMNet acepta waveform mono 16 kHz y produce embeddings/scores | FACT/EVIDENCE | TensorFlow YAMNet docs | baseline de preprocessing/model A |
| EV-002 | YAMNet usa patches ~0.96 s con hop ~0.48 s | FACT/EVIDENCE | TensorFlow/YAMNet | floor de latencia observado; no garantiza E2E |
| EV-003 | AudioSet es corpus/ontología amplia usada por YAMNet/PANNs | FACT/EVIDENCE | Google AudioSet | prior semántico/pretraining |
| EV-004 | PANNs ofrece modelos preentrenados AudioSet y variantes frame-wise | FACT/EVIDENCE | paper/repo PANNs | challenger B |
| EV-005 | Frigate implementa audio detection en cámaras y MQTT | FACT/EVIDENCE | Frigate docs | patrón de arquitectura validado por ecosistema |
| EV-006 | go2rtc puede restream/fan-out streams | FACT/EVIDENCE | go2rtc repo | relay opcional |
| EV-007 | MQTT define QoS 0/1/2 | FACT/EVIDENCE | MQTT spec | idempotencia requerida con QoS1 |
| EV-008 | FSD50K tiene licencias por clip heterogéneas | FACT/EVIDENCE | FSD50K release | license manifest obligatorio |
| EV-009 | ESC-50/UrbanSound8K son NC en sus releases principales | FACT/EVIDENCE | dataset repos/releases | benchmark académico, no asumir ruta comercial |
| EV-010 | SONYC es sensor network urbano multilabel | FACT/EVIDENCE | SONYC release/paper | referencia multi-source/polyphony |
| EV-011 | MIMII modela ruido/maquinaria industrial y domain conditions | FACT/EVIDENCE | MIMII | robustness reference |
| EV-012 | RTSP/ONVIF son caminos comunes de streaming en cámaras IP | FACT/EVIDENCE | ONVIF/FFmpeg docs | ingest candidate |
| EV-013 | in-toto/Sigstore/SLSA cubren attestations/provenance | FACT/EVIDENCE | official docs | evitar blockchain propia |
| EV-014 | Domain shift probablemente domine error real | INFERENCE | datasets + field systems | field dataset obligatorio |
| EV-015 | Multi-label es más natural en audio ambiental superpuesto | INFERENCE | AudioSet/FSD50K/SONYC | sigmoid candidate |
| EV-016 | 10–15 m podría ser nominal para algunos sonidos fuertes | HYPOTHESIS | acústica + diseño PoC | medir 5–25 m |
| EV-017 | MQTT/Mosquitto es suficiente para MK1 | DECISION_CANDIDATE | MQTT ecosystem | benchmark operacional antes MK2 |

Este ledger no sustituye una citation formal en trabajos académicos; conserva provenance de ingeniería.