# Decision Log

**Status:** `ACTIVE_LEDGER`

## 1. Purpose

This ledger records engineering decisions that affect ECHO's scope, architecture, scientific validity or operations. It intentionally separates decisions from empirical outputs. A model winner, numerical threshold or supported source count is not “decided” before measurement; it remains an empirical node.

## 2. State semantics

`OPEN` means a decision still requires evidence or owner action. `CANDIDATE` is plausible but not frozen. `CLOSED` means the choice is frozen within a stated scope. `CLOSED (REJECTED)` records an alternative deliberately not selected. `CLOSED (DEFERRED)` records a valid option intentionally moved to a later milestone. `EXTERNAL_GATE_OPEN` depends on hardware, permission or another external condition. `INVALIDATED` means an upstream dependency changed.

## 3. Decisions

| ID | Decision | State | Rationale/evidence | Downstream effect |
|---|---|---|---|---|
| D-001 | fixed ECHO promise | CLOSED | owner/project charter | constrains every MK |
| D-002 | classify acoustic observations, not crimes/social causes | CLOSED | semantic verifiability | taxonomy/event claims |
| D-003 | logical multi-source from MK1 | CLOSED | avoids single-camera redesign | source contract/runtime |
| D-004 | PoC may use one physical source | CLOSED | lowers external dependency without changing interfaces | demo/field plan |
| D-005 | RTSP primary camera ingest interface | CLOSED | camera ecosystem + FFmpeg/GStreamer support; actual camera still external | adapters/deployment |
| D-006 | ONVIF optional, not hard dependency | CLOSED | explicit RTSP must remain usable without discovery | source discovery |
| D-007 | FFmpeg baseline decoder/normalizer | CLOSED | mature codec/RTSP support and simple PoC integration | MK1 ingest |
| D-008 | GStreamer fallback/challenger; go2rtc optional relay | CLOSED | use only if reconnect/jitter/fan-out evidence justifies extra layer | deployment complexity |
| D-009 | MQTT + Mosquitto bus for MK1 | CLOSED | lightweight pub/sub, QoS, self-hosted, comparable operational precedent | event delivery |
| D-010 | YAMNet + ECHO head = benchmark A | CLOSED | official transfer-learning path and compact embeddings | benchmark |
| D-011 | PANNs/Cnn14 = benchmark B | CLOSED | strong AudioSet-pretrained representation | benchmark |
| D-012 | compact log-mel CNN = benchmark C | CLOSED | scientific control without large pretrained backbone | benchmark |
| D-013 | AST/HTS-AT/PaSST/BEATs not mandatory in first benchmark | CLOSED (DEFERRED) | avoid expanding experiment before A/B/C evidence; retain as challengers | MK2/extended |
| D-014 | target output is multi-label | CLOSED | concurrent acoustic events are plausible; polyphonic SED precedent | head/loss/metrics |
| D-015 | no monolithic forced `OTHER` | CLOSED | use background, explicit hard negatives and abstention | data/decision layer |
| D-016 | temporal Event Engine between inference and alerts | CLOSED | users need physical events, not overlapping-window scores | event lifecycle |
| D-017 | per-class thresholds derived from validation | CLOSED | score distributions differ; no magic global threshold | calibration/test |
| D-018 | continuous raw audio retention off by default | CLOSED | minimization; not needed by promise | privacy/storage |
| D-019 | evidence DAG rather than blockchain | CLOSED | Git/hashes/manifests/CI satisfy provenance/invalidation needs | governance |
| D-020 | code license | OPEN_OWNER_DECISION | Apache-2.0 preferred candidate; owner must explicitly choose | release only |
| D-021 | exact camera/profile/codecs | EXTERNAL_GATE_OPEN | requires professor hardware/access | field branch |
| D-022 | MK1 target classes v1 | CLOSED | `GLASS_SHATTER`, `SIREN`, `FIRE_ALARM`, `VEHICLE_HORN`, `TIRE_SQUEAL` | data/head/events |
| D-023 | guaranteed distance | EXTERNAL_GATE_OPEN | cannot be known without device/site/SNR tests | field requirement |
| D-024 | final SLO values | OPEN_EMPIRICAL | depend on MK1 measurements | MK2 design |
| D-025 | common A/B/C benchmark protocol | CLOSED | same manifest/splits/hardware/calibration protocol | model selection |
| D-026 | Redis Pub/Sub as alarm bus | CLOSED (REJECTED) | ephemeral Pub/Sub behavior mismatches desired disconnect/delivery reasoning | avoids wrong bus |
| D-027 | MQTT QoS1 for confirmed events/alerts | CLOSED | at-least-once with explicit consumer idempotency | `event_id` required |
| D-028 | PSDS/event metric secondary when strong labels exist | CLOSED | useful for polyphonic temporal evaluation but not replacement for operational metrics | evaluation |
| D-029 | `VEHICLE_COLLISION` not in MK1 taxonomy | CLOSED (DEFERRED) | generic impact does not prove collision; requires specific corpus/definition | taxonomy |
| D-030 | buffers/queues must be bounded | CLOSED | protects freshness/memory under overload | runtime |
| D-031 | source state keyed by source_id + event_type | CLOSED | prevents cross-camera state leakage | Event Engine |
| D-032 | field holdout untouched during model/threshold selection | CLOSED | domain validity | data/benchmark |
| D-033 | asset-level provenance/license/hash | CLOSED | mixed licenses and reproducibility | data admission |
| D-034 | live overload is observable and freshness-aware | CLOSED_FOR_ARCH | stale alerts are harmful; exact drop policy remains empirical | scheduler |

## 4. Empirical nodes, not architecture indecision

The following remain open because the build/test phase must produce them:

```text
EMP-MODEL-001    model winner
EMP-THRESH-001   numerical per-class thresholds
EMP-CAP-001      supported N-source envelope
EMP-DIST-001     distance/SNR envelope
EMP-SLO-001      final service/quality objectives
```

They do not justify reopening upstream design unless their results show the architecture is infeasible.

## 5. Decision evidence rule

A CLOSED decision must reference at least one of: project charter/owner constraint, primary source evidence, reproducible experiment, validated contract dependency or explicit trade-off. “Common practice” alone is not sufficient.

## 6. Alternatives and reversibility

Reversible choices such as FFmpeg vs GStreamer are deliberately abstracted behind contracts. Hard-to-reverse choices such as taxonomy semantics, source identity and event lifecycle receive stricter gates because they fan out into data, models and consumers.

## 7. Invalidation examples

Changing MK1 taxonomy invalidates label mappings, heads, manifests, benchmark comparability, thresholds and event-type consumers. Changing camera hardware does not invalidate the taxonomy but may invalidate field compatibility and distance evidence. Changing MQTT semantics can invalidate consumer delivery tests without invalidating acoustic model scores.

## 8. Maintenance

Every new material decision receives a stable ID. Replaced decisions are not deleted; they remain historical and point to the successor/version that supersedes them.