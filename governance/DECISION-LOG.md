# Decision Log

**Status:** `ACTIVE_LEDGER`

## 1. Purpose

This ledger records engineering decisions that affect ECHO's scope, architecture, scientific validity or operations. It separates decisions from empirical outputs. A model winner, numerical threshold or supported source count is not decided before measurement; it remains an empirical node.

## 2. State semantics

`OPEN` requires evidence or owner action. `CANDIDATE` is plausible but not frozen. `CLOSED` is frozen within scope. `CLOSED (REJECTED)` records a deliberately rejected alternative. `CLOSED (DEFERRED)` preserves an option moved to a later milestone. `EXTERNAL_GATE_OPEN` depends on hardware, permission or another external condition. `INVALIDATED` means an upstream dependency changed.

## 3. Decisions

| ID | Decision | State | Rationale/evidence | Downstream effect |
|---|---|---|---|---|
| D-001 | fixed ECHO promise | CLOSED | owner/project charter | constrains every MK |
| D-002 | classify acoustic observations, not crimes/social causes | CLOSED | semantic verifiability | taxonomy/event claims |
| D-003 | logical multi-source from MK1 | CLOSED | avoids single-camera redesign | source contract/runtime |
| D-004 | PoC may use one physical source | CLOSED | lowers external dependency without changing interfaces | demo/field plan |
| D-005 | RTSP primary camera ingest interface | CLOSED | ecosystem + FFmpeg/GStreamer support; actual camera external | adapters/deployment |
| D-006 | ONVIF optional | CLOSED | explicit RTSP usable without discovery | discovery |
| D-007 | FFmpeg baseline decoder | CLOSED | mature codec/RTSP support and simple PoC integration | MK1 ingest |
| D-008 | GStreamer fallback; go2rtc optional relay | CLOSED | only add complexity when evidence justifies it | deployment |
| D-009 | MQTT + Mosquitto bus for MK1 | CLOSED | lightweight QoS pub/sub and operational fit | event delivery |
| D-010 | YAMNet + ECHO head = A | CLOSED | official transfer-learning path | benchmark |
| D-011 | PANNs/Cnn14 = B | CLOSED | strong AudioSet representation | benchmark |
| D-012 | compact log-mel CNN = C | CLOSED | scientific control | benchmark |
| D-013 | transformers/SSL not mandatory in first benchmark | CLOSED (DEFERRED) | retain as challengers without exploding MK1 | extended/MK2 |
| D-014 | target output multi-label | CLOSED | concurrent events/polyphonic SED | head/loss/metrics |
| D-015 | no forced monolithic OTHER | CLOSED | background + hard negatives + abstention | data/decision layer |
| D-016 | temporal Event Engine between model and alerts | CLOSED | window scores are not physical events | lifecycle |
| D-017 | per-class thresholds from validation | CLOSED | score distributions differ | calibration |
| D-018 | continuous raw audio retention off | CLOSED | minimization; not required by promise | privacy |
| D-019 | evidence DAG, not blockchain | CLOSED | Git/hashes/manifests/CI are sufficient | governance |
| D-020 | code license | OPEN_OWNER_DECISION | Apache-2.0 preferred candidate | release |
| D-021 | exact camera/profile/codecs | EXTERNAL_GATE_OPEN | professor/hardware | field branch |
| D-022 | MK1 taxonomy v1 | CLOSED | five observable targets | data/head/events |
| D-023 | guaranteed distance | EXTERNAL_GATE_OPEN | device/site/SNR measurement | field requirement |
| D-024 | final SLOs | OPEN_EMPIRICAL | require MK1 evidence | MK2 |
| D-025 | common A/B/C protocol | CLOSED | same manifests/splits/hardware/calibration | model selection |
| D-026 | Redis Pub/Sub as alarm bus | CLOSED (REJECTED) | ephemeral semantics not preferred for required delivery reasoning | delivery |
| D-027 | MQTT QoS1 confirmed events/alerts | CLOSED | at-least-once + explicit idempotency | event_id |
| D-028 | PSDS secondary with strong labels | CLOSED | temporal/polyphonic metric, not operational replacement | evaluation |
| D-029 | vehicle collision label in MK1 | CLOSED (DEFERRED) | generic impact does not prove collision | taxonomy |
| D-030 | queues/buffers bounded | CLOSED | prevents memory/latency spiral | runtime |
| D-031 | Event Engine state keyed by source+event | CLOSED | prevents cross-source state leakage | runtime |
| D-032 | field holdout untouched during selection | CLOSED | domain validity | benchmark |
| D-033 | asset provenance/license/hash required | CLOSED | reproducibility + mixed license control | data admission |
| D-034 | live overload observable/freshness-aware | CLOSED_FOR_ARCH | stale alerts are harmful; numeric policy empirical | scheduler |

## 4. Empirical nodes

```text
EMP-MODEL-001    model winner
EMP-THRESH-001   numerical thresholds
EMP-CAP-001      supported N-source envelope
EMP-DIST-001     distance/SNR envelope
EMP-SLO-001      final SLOs
```

These are outputs of MK1/MK2 tests, not excuses to guess before build.

## 5. Evidence rule

A CLOSED decision must be supported by project authority, primary-source evidence, a reproducible experiment, validated dependency or an explicit trade-off. Popularity/common practice alone is insufficient.

## 6. Reversibility

Reversible implementation choices are hidden behind contracts. Hard-to-reverse semantic choices such as taxonomy, source identity and event lifecycle receive stricter review because they fan out into data, models, APIs and consumers.

## 7. Invalidation examples

Changing taxonomy invalidates label mappings, heads, manifests, benchmark comparability, thresholds and event consumers. Changing camera hardware may only invalidate field compatibility/distance claims. Changing MQTT semantics may invalidate delivery tests while leaving acoustic model evidence valid.

## 8. Maintenance

Every material new decision receives a stable ID. Superseded decisions remain historical and reference the new decision/version rather than being deleted.