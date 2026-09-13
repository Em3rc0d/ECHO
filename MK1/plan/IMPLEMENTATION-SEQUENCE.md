# MK1 Implementation Sequence

**Status:** `FROZEN_ORDER / BUILD_NOT_STARTED`

## Phase 1 — repository/runtime skeleton

Create package/module boundaries matching architecture, config/schema validation, structured logging, dependency lock and test harness. No neural-model complexity before deterministic source/audio path works.

## Phase 2 — data/replay

Implement manifest loader, group/split verification, replay source, normalized audio/window contract and golden fixtures.

## Phase 3 — baseline model interfaces

Implement common ModelRunner contract and A/B/C adapters. Verify identical target score schema and frozen dataset splits.

## Phase 4 — benchmark/calibration

Train/evaluate arms, record result bundles, calibrate thresholds on validation, preserve frozen test predictions/error analysis.

## Phase 5 — Event Engine

Implement deterministic per-source/type state machine, temporal config and lifecycle tests. Tune only on validation/replay development data.

## Phase 6 — Pub/Sub and persistence

Implement MQTT publisher/subscriber, event schema, idempotency and minimal structured result store/query.

## Phase 7 — streaming/multi-source/failures

Long negative/positive replay, concurrent sources, overload/reconnect/broker failures and runtime profiling.

## Phase 8 — camera integration

When external gate closes, add RTSP adapter/probe and field evaluation without modifying downstream semantics.

## Phase 9 — certification

Freeze selected model/config, rerun full suite, document limitations and emit MK1 certificate or explicit failures.

## Stop-the-line

Leakage, incompatible license, contract drift or hidden unbounded buffering stops downstream work until corrected.