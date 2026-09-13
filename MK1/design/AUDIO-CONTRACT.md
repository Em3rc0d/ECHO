# Audio Contract — MK1

**Status:** `FROZEN_BASELINE / MODEL-SPECIFIC FRONTENDS VERSIONED`

## Purpose

Create a deterministic boundary between heterogeneous source audio and model/window processing.

## Canonical baseline

Decoded source audio is converted to mono PCM/float samples under a versioned normalization policy. YAMNet baseline requires 16 kHz mono waveform; other candidates may have model-specific frontend adapters while consuming the same underlying admitted audio.

## Audio frame metadata

```yaml
source_id: ...
stream_generation: ...
sequence: ...
received_at: ...
media_time: optional
original_codec: optional
original_sample_rate: optional
original_channels: optional
normalized_sample_rate: ...
sample_count: ...
preprocessing_version: ...
```

## Windowing

Window size/hop are explicit config tied to model/frontend version. YAMNet's referenced implementation uses overlapping frames; PANNs/custom CNN may require different windows. Event Engine sees timestamped inference records, not raw model frame assumptions.

## Signal processing policy

Resample/downmix deterministically. Avoid hidden AGC/noise filtering unless versioned and benchmarked. Record clipping/silence/level diagnostics as telemetry where useful, not as target labels.

## Buffering

Per-source buffers are bounded. Live mode favors freshness and explicit stale/drop metrics; offline benchmark mode may block to guarantee complete deterministic processing.

## Risks

Resampling artifacts, stereo cancellation during downmix, source AGC, low bitrate codecs, clipping and timestamp drift can change transient target quality.

## Validation

Golden audio fixtures verify deterministic resample/downmix/window timestamps. Codec/sample-rate ablations evaluate target sensitivity.

## Invalidation

A changed canonical sample format/preprocessing version invalidates benchmark comparability for affected models.