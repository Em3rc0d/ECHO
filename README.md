# ECHO

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

**Project status:** documentation-first, MK0 certified, MK1 replay build ready.  
**Scope authority:** `PROJECT-CHARTER.md`  
**Current state:** `CURRENT-STATE.md`

## 1. What ECHO is solving

ECHO transforms continuous, unstructured environmental audio into machine-readable acoustic observations and temporally consolidated events. Its value is not merely running a neural network on a clip; it is maintaining a reproducible path from a physical/logical audio source to a classified acoustic event with provenance, confidence, source identity, timing and downstream delivery.

The product intentionally stays at the level of observable acoustic evidence. It may classify `SIREN`, `GLASS_SHATTER` or `VEHICLE_HORN`; it does not claim that a robbery, traffic accident or emergency occurred solely because a sound was detected.

## 2. Fixed product promise

The following sentence is immutable within this repository:

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

Cameras, NVRs, RTSP/ONVIF, FFmpeg/GStreamer, MQTT, storage, dashboards and notifications are supporting infrastructure. They may change without redefining ECHO.

## 3. Milestone method

Every milestone uses the same engineering pipeline:

```text
brainstorming -> design -> arch -> plan -> build -> test
```

and contains two evidence workspaces:

```text
mining-site/   evidence, provenance, manifests, external facts
quarries/      research questions -> synthesis -> decisions -> validation
```

### MK0 — research and uncertainty reduction

MK0 collects state-of-the-art evidence, datasets, model families, comparable systems, protocols, licensing constraints, risks and test methodology. It can certify research/design choices but never invent empirical product results.

### MK1 — first vertical

MK1 builds a reproducible path from dataset/replay and later a real camera source through decoding, normalization, inference, Event Engine and MQTT delivery. It produces the first empirical model/threshold/runtime evidence.

### MK2 — robust product

MK2 hardens the MK1 vertical into a multi-source operable product: capacity, backpressure, resilience, observability, model governance, security, deployment, rollback and release certification.

## 4. Reference architecture

```text
Audio Source(s)
  IP camera / NVR / microphone / deterministic replay
                  |
                  v
             Source Registry
           source_id + metadata
                  |
                  v
        RTSP/File Ingestion Adapter
             FFmpeg baseline
                  |
                  v
       Decode -> mono PCM -> normalize
                  |
                  v
       bounded per-source audio buffer
                  |
                  v
             Window Producer
                  |
                  v
           Inference Scheduler
                  |
          +-------+-------+
          | model workers |
          +-------+-------+
                  |
                  v
       RAW_INFERENCE(source_id,...)
                  |
                  v
        Temporal Event Engine
          threshold / evidence
         hysteresis / dedup
                  |
                  v
          CONFIRMED_EVENT
                  |
        +---------+---------+
        |                   |
        v                   v
 MQTT/Mosquitto       persistence/query
        |
        v
 subscribers / alerts
```

The architecture is logically multi-source from the first build. A one-camera PoC validates connectivity, not the maximum supported source count.

## 5. MK1 scientific baseline

The minimum model benchmark is intentionally comparative:

```text
A  YAMNet embeddings + ECHO head
B  PANNs/Cnn14 + ECHO head
C  compact ECHO log-mel CNN
```

Extended transformer/self-supervised candidates such as AST, HTS-AT, PaSST and BEATs remain research challengers. No model becomes the winner from an external leaderboard alone; ECHO measures its own taxonomy, data splits, long-stream false alarms, latency and hardware cost.

The frozen MK1 v1 target taxonomy is:

```text
GLASS_SHATTER
SIREN
FIRE_ALARM
VEHICLE_HORN
TIRE_SQUEAL
BACKGROUND_NO_TARGET
UNKNOWN  # decision-layer abstention state
```

## 6. Event semantics

A model produces scores per analysis window. Users and downstream systems consume events. ECHO therefore separates:

```text
RAW_INFERENCE
    -> CANDIDATE_EVENT
    -> CONFIRMED_EVENT
    -> ALERT / PUBSUB
```

The Event Engine owns temporal confirmation, hysteresis/debounce, deduplication, cooldown and event closure. Threshold values are empirical outputs of validation and replay tests, never magic constants frozen in documentation.

## 7. Data governance

Every admitted training/evaluation audio asset must have provenance, release/source identity, hash, license/permitted use, original label, ECHO mapping and group/split metadata. Splits are group-aware to reduce leakage across original recording, physical event, uploader/source, site or device.

A public dataset is not treated as a proxy for production. ECHO maintains an untouched field holdout once authorized real-device recordings exist. Hard negatives are explicit confuser families rather than a single infinite `OTHER` bucket.

## 8. Runtime and multi-source invariants

`source_id` flows through decoding, buffers, windows, inference, Event Engine state, event envelope and telemetry. Buffers and queues are bounded. A failed/noisy source must not terminate or starve unrelated sources. Capacity is measured by load/soak tests and is not inferred from a short demo.

## 9. Pub/Sub semantics

MK1 uses MQTT/Mosquitto as the initial event bus. Confirmed events and alerts use QoS 1 as a frozen build contract, which means consumers must tolerate duplicate delivery. `event_id` is the idempotency key. State and telemetry topics have separate retention/QoS semantics documented in the Pub/Sub artifacts.

## 10. Privacy and security baseline

ECHO does not require continuous speech recognition, speaker identification or voice profiling. Continuous raw audio retention is off by default. Real field capture is an external/privacy gate that must document authorization, purpose, access and retention. Camera/broker credentials are never committed to Git.

## 11. Evidence and certification

ECHO uses a dependency DAG rather than blockchain. Each important decision has upstream evidence and downstream consumers. If an upstream contract or taxonomy changes, dependent certificates are reviewed and can become `INVALIDATED`.

```text
Evidence -> Design -> Architecture -> Plan -> Build -> Test -> Certificate
```

Git preserves document history; model/data/build artifacts additionally require hashes/manifests. Future CI may generate attestations and provenance.

## 12. Repository navigation

- `PROJECT-CHARTER.md` — immutable promise, scope boundaries and project laws.
- `CURRENT-STATE.md` — active milestone/gate status.
- `REPOSITORY-MAP.md` — semantic ownership of every repository area.
- `MK0/` — research and certified pre-build evidence.
- `MK1/` — first vertical specification/build/test artifacts.
- `MK2/` — robust-product specification and release gates.
- `research/` — consolidated model/dataset/related-system evidence.
- `governance/` — decisions, risk, DoR/DoD, certificates and external gates.
- `schemas/` — machine-readable event/source contracts.
- `THIRD_PARTY.md` — dependency/model/dataset license governance.

## 13. Current known uncertainty

The remaining high-value unknowns are deliberately empirical or external: exact model winner, numerical thresholds, false-alarm profile, latency/capacity, field distance/SNR envelope and characteristics/access of the professor-provided camera. They are not “missing documentation”; they are controlled experiments or external gates.

## 14. Build rule

> **Do not implement around an unresolved architecture-changing decision.**

MK1 replay build is currently authorized because those core decisions have been closed. Any new implementation must preserve the frozen contracts or explicitly reopen and recertify the affected node.