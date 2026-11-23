# MK1 — Exact-zero and invalid-PCM pre-inference boundary

**Status:** `IMPLEMENTED / LOCAL SOURCE-MATCHED QA 18/18 PASS / DOCKER-MODEL-RTSP NOT CERTIFIED`  
**Date:** 2026-11-22  
**Scope:** `ECHO-MVP-001` — three classes; issue #53  
**Authoritative gate:** `MK1/test/FIELD-AUDIO-ROBUSTNESS-GATE.md`

## Purpose

Prevent the **known deterministic** zero-input activation of
`GLASS_SHATTER ≈ 0.562044` from reaching the selected scorer and temporal
confirmation logic in **uncalibrated external WAV/microphone analysis** and
**diagnostic RTSP worker**.

This is a containment of a proven input-validity defect, **not** proof of
environmental/OOD rejection or field-calibrated sound classification.

## Frozen boundaries

- No model weights/backbones/threshold changes; no new target classes.
- Default `EchoReplayPipeline` behavior is **unchanged** unless
  `signal_quality_gate_enabled=True` is explicitly passed.
- The controlled professor scenarios remain governed by their existing replay
  behavior; external/unvalidated audio gets the new gate.
- No operational target alert, approved upstream acceptance profile, or
  production MQTT publication is enabled.
- Operator remains lab diagnostic; RTSP worker still only emits snapshots.
- No host-installed Python/FFmpeg dependencies added to ECHO runtime; Docker
  remains mandatory for operational verification.

## Deterministic state semantics

| Condition | State | Inference action |
|---|---|---|
| At least one sample, all exact zero (positive/negative signed zero) | `NO_SIGNAL` | No scoring; reset candidate/close active temporal state |
| Empty, nonnumeric, NaN or ±Infinity PCM | `INVALID_SIGNAL` | No scoring; reset candidate/close active temporal state |
| All finite PCM containing at least one nonzero sample | `UNASSESSED_NONZERO` | Allow scoring **without implying valid field acoustics** |
| No full windows | `NO_WINDOWS` (replay summary) | No scoring; prior minimum-duration external-demo guard remains |

The boundary **intentionally does not invent a dBFS/RMS/peak threshold**.
Near-silence, one-LSB codec residue, frozen nonzero streams, clipping, device
gain faults, speech/traffic/music confusers and OOD detection remain unresolved.

`NO_SIGNAL` is distinct from `NO_TARGET`: no usable signal cannot
certify that there was no target acoustic event. If a recording mixes
scored and rejected windows without confirmed targets, the external demo
returns `INCOMPLETE_SIGNAL`, not the misleading all-interval `NO_TARGET`.

## Runtime implementation

- `src/echo/runtime/signal_quality.py`: deterministic per-window quality
  inspection, standard-library only.
- `src/echo/runtime/pipeline.py`: opt-in pre-scorer gate; reject counts and
  `signal_quality_state` in summary; on rejected windows, call
  `TemporalEventEngine.close_session` to discard candidates and close active
  diagnostic events; do not bridge gaps.
- `demo/server.py`: opt-in only for external audio. Returns `NO_SIGNAL`,
  `INVALID_SIGNAL`, or `INCOMPLETE_SIGNAL` instead of misrepresenting an
  unanalysable interval as a fully supported `NO_TARGET`.
- `demo/index.html`: displays signal state, number of inferred/rejected
  windows and keeps target event publication suppressed.
- `scripts/emulator/echo_rtsp_live_worker.py`: checks PCM **before**
  acquiring shared scorer lock; on rejected PCM resets temporal state, clears
  scores/envelope and records diagnostics without refreshing `at` or
  `window_end_utc` (last-inference timestamps).
- Operator gateway/web: validates and shows quality status and rejected-window
  counters independently from inference freshness.

## Verification plan (partially executed)

Local source-matched unit/FFmpeg regression results: **18/18 PASS, 0 skipped**.
The nine Python source/test files run locally have exact Git blob hashes
matching the corresponding files in the PR; however this was a reconstructed
subset, **not a full PR checkout or Docker run**. Reproducibility record:
`MK1/test/SIGNAL-QUALITY-LOCAL-QA-2026-11-22.md`.

The new optional FFmpeg tests are in
`tests/runtime/test_signal_quality_ffmpeg.py` and generate their own WAVs.

1. Pure unit regression, no model, no audio assets:
   `PYTHONPATH=src python -m unittest tests.runtime.test_signal_quality -v`
2. Existing runtime and temporal regressions:
   `PYTHONPATH=src python -m unittest tests.runtime.test_event_engine tests.runtime.test_replay -v`
3. RTSP supervision regression with local test deps:
   `PYTHONPATH=src python -m unittest tests.emulator.test_rtsp_supervision -v`
   and newly defined synthetic signal-path test:
   `PYTHONPATH=src python -m unittest tests.emulator.test_signal_quality_rtsp -v`
   (2 new cases, **NOT EXECUTED** locally).
4. Demo v2 decision regression, no model weights:
   `PYTHONPATH=src python -m unittest tests.runtime.test_demo_signal_policy -v`
   (7 new cases, **NOT EXECUTED** locally).
5. Operator compile/build and gateway automated suite under a disposable
   correctly provisioned local stack, then human acceptance cases O01–O33.
6. **Docker with real checkpoint:** a 60 s exact-zero external WAV must yield
   `NO_SIGNAL`, zero scored windows, zero internal candidates and zero
   accepted or published target events. Confirm governed controlled scenarios
   remain byte-for-byte contract compatible.
7. **Emulated RTSP:** exact-zero/silence → quality rejected; transition
   valid → zero → valid must not reuse temporal candidates; silence must not
   refresh the last-inference timestamp; all other camera workers progress.
8. **Holdout/field gate remains OPEN:** measure signal validity and false
   alarms per source-hour on diverse independently held-out audio. A near-zero
   level threshold must be calibrated on development evidence only.

## Quality acceptance checklist

- [x] 8/8 new Python signal-quality unit regressions PASS on source-matched subset
- [x] 8/8 existing Event Engine + replay regressions PASS on source-matched subset
- [x] 2/2 FFmpeg-generated WAV decoding/regression tests PASS locally
- [ ] 7 demo-v2 unit tests PASS (defined, not executed)
- [ ] 2 new fake-RTSP signal-integrity tests PASS (defined, not executed)
- [ ] Full exact-PR-checkout tests in Docker PASS
- [ ] Operator/gateway compilation and tests PASS
- [ ] Docker exact-zero PANNs regression PASS
- [ ] Controlled professor demo unchanged PASS
- [ ] RTSP four-source silence/recovery observation PASS
- [ ] No fabricated `NO_TARGET` or target MQTT/alert PASS
- [ ] Quality metrics/provenance recorded with SHA, config, source and time
- [ ] Independent environmental holdout evaluated to predeclared criteria

The 32 kHz, 6 s-window synthetic microbenchmark showed ~12 ms median
per quality scan over 192,000 samples on the local runner; this is not a
multi-source load/SLO measurement. A 1-LSB nonzero signal is correctly
left `UNASSESSED_NONZERO`, illustrating why field-level low-signal
thresholds must be calibrated rather than guessed.

**Current decision: HOLD / NOT CERTIFIED.** Do not merge or treat issue #53
as closed on the strength of source code or isolated unit tests.
