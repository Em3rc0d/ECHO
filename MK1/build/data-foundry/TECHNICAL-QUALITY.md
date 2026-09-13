# Data Foundry — Technical Quality, Audio Probe and Duplicate Evidence

**Status:** `IMPLEMENTED`

## Purpose

`DF-G4` and `DF-G5` require evidence from the actual bytes, not only CSV metadata. An asset may have valid labels and rights yet still be unusable because the file is missing/corrupt, has no audio stream, exposes invalid technical metadata or leaks into evaluation through duplicates.

## Audio probe

`src/echo/data_foundry/probe.py` probes the local asset before admission. PCM-compatible WAV is inspected through Python's standard `wave` parser. Other codecs, and WAV variants unsupported by `wave`, fall back to `ffprobe` when available.

The probe records:

```text
ok
backend
duration_seconds
sample_rate_hz
channels
codec_name
failure reason
```

Missing or unprobeable audio adds `AUDIO_PROBE_FAILED` and quarantines the asset. When upstream metadata omits duration/sample-rate/channels, verified probe values populate the canonical record. Conflicting declared vs observed technical metadata is retained as audit evidence rather than silently erased.

## Canonical identity vs perceptual screening

Two different concepts are kept separate:

- `sha256`: byte-identity and immutable asset identity;
- `near_duplicate_fingerprint`: screening signal for acoustically equivalent/similar content.

The Foundry includes `pcm_wav_envelope_v1`, a gain-normalized temporal-envelope fingerprint for PCM WAV screening. It is intentionally conservative and does not claim state-of-the-art audio fingerprint equivalence. Unsupported formats can later receive a decoder-derived fingerprint without changing manifest semantics.

## Duplicate gates

Before freeze:

```text
same recording_group_id across protected splits -> FAIL
same SHA-256 across protected splits            -> FAIL
same registered near fingerprint across splits  -> FAIL
same SHA-256 with conflicting ECHO labels        -> FAIL / review upstream
```

Exact duplicates inside one split may be reported without automatically failing, because some releases legitimately reference identical media multiple times; downstream policy can decide whether to collapse them. Conflicting labels over identical bytes always require resolution.

## Why no silent repair

The Foundry does not transcode a corrupt source and pretend the original passed. Repair/transcode, if needed, must create a derived asset with parent lineage and a new SHA-256. The original evidence remains quarantined/rejected.

## Testing

CI includes valid PCM-WAV probe tests, corrupt-audio quarantine, gain-scaled near-fingerprint behavior, group leakage, exact duplicate leakage, near-duplicate leakage and exact-byte label-conflict stop-the-line tests.

## Invalidation

Changing probe backend semantics, fingerprint algorithm/version, blocking quality reasons or duplicate-conflict rules changes Foundry evidence semantics and requires re-running the toolchain test/certificate and affected real corpus freeze.
