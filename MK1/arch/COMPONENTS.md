# MK1 Components

**Status:** `FROZEN_RESPONSIBILITIES`

## SourceRegistry

Stores configured logical sources and metadata/secret references. It never stores plaintext credentials in persisted repo config.

## SourceSupervisor

Owns source lifecycle, adapter instance, reconnect/backoff, stream generation and health. One supervisor failure must not kill unrelated sources.

## SourceAdapter

Replay/RTSP implementation that emits decoded/decodable audio plus timing/source metadata. Adapter-specific details stop here.

## AudioNormalizer / WindowProducer

Deterministic resample/downmix/normalization and model-window generation. Versioned preprocessing is part of benchmark identity.

## InferenceScheduler

Bounded work queue, per-source fairness and freshness policy. Offline mode can run complete/no-drop; live mode exposes stale/drop behavior.

## ModelRunner

Loads a selected model artifact and produces target score vectors with model/preprocessing identity. A/B/C implementations conform to same output contract.

## EventEngine

Consumes ordered inference records, applies validated per-class temporal rules and emits stable event IDs/lifecycle changes.

## Publisher

Maps confirmed event/state/telemetry schemas to MQTT topics/QoS. It does not decide whether an acoustic event is true.

## Event/Result Store

MK1 persistence can be simple but must retain enough structured evidence for E2E queries/test analysis. Raw continuous audio is not required.

## Observability

Cross-cutting metrics/log interfaces collect source health, queue/runtime, inference/event and broker status with secret/media minimization.

## Dependency rule

Components communicate through explicit interfaces; no module reaches into another module's mutable state as a shortcut.

## Invalidation

Merge/split components freely only if responsibility and contracts remain intact; semantic ownership changes require architecture review.