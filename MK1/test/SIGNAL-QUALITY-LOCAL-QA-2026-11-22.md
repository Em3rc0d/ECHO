# ECHO MK1 — Source-matched isolated QA execution (2026-11-22, Lima)

**Status:** `LAB REGRESSION PASS / INCOMPLETE CERTIFICATION`  
**PR:** #58, `fix/mk1-signal-quality-gate-20261122`  
**Scope:** only the listed matched Python files and synthetic FFmpeg WAV tests  
**Security:** no private recordings, camera credentials or model weights used

## Environment

- Linux x86_64, Python 3.13.5
- FFmpeg `7.1.5-0+deb13u1`
- Docker executable **not available** in this environment
- GitHub remote unavailable over network from the test shell. Relevant files
  were obtained through the connected GitHub file API and reconstructed
  in a local test directory. Each of the nine run files matched its remote
  **Git blob SHA**, preventing approximation of those source files.

## Exact local verification command

```bash
PYTHONPATH=src python3 -m unittest \
  tests.runtime.test_signal_quality \
  tests.runtime.test_event_engine \
  tests.runtime.test_replay \
  tests.runtime.test_signal_quality_ffmpeg -v
```

Observed output:

```text
Ran 18 tests in 1.911s

OK
```

- New signal-quality Python tests: **8/8 PASS**
- Original Event Engine regression tests: **6/6 PASS**
- Original replay regression tests: **2/2 PASS**
- New FFmpeg/WAV decode integration tests: **2/2 PASS**
- **0 errors, 0 failures, 0 skipped** in the local execution

The FFmpeg smoke decodes an independently generated 60s 32kHz mono
PCM16 exact-zero WAV into 55 complete 6-second/1-second-hop windows.
All 55 windows yield `NO_SIGNAL`; scored windows = 0; calls to a
synthetic high-glass scorer = 0; emitted target events = 0.
A 7s generated nonzero sine control gives 2 completed windows,
both scored, and `UNASSESSED_NONZERO` rather than an invented
near-silence quality verdict.

The fake scorer returns `GLASS_SHATTER=0.5620440244674683` **only if
invoked**. It is **not** the actual PANNs inference model. The zero
case proves this synthetic scorer is *not invoked*, not that PANNs
field false positives are resolved.

## Matched source/test Git blob SHA-1 identities

| Git repository path | Git blob SHA-1 |
|---|---|
| `src/echo/modeling/audio.py` | `9916d0cb859e0655ca5f96bcc5b30c32541c532c` |
| `src/echo/runtime/event_engine.py` | `da3754b7dab32a87ef6610d304f41ee0f1aebd50` |
| `src/echo/runtime/pipeline.py` | `04f5b040e88dcb04a230e4abac805daf36896c1d` |
| `src/echo/runtime/replay.py` | `9197ca6418feeea840a734ebc0f033483fbb04d8` |
| `src/echo/runtime/signal_quality.py` | `ba29b411861599221e724f529924da0c6b698aab` |
| `tests/runtime/test_event_engine.py` | `0cff4e34c902bb6d9266aeb2d2125ef2bb657cd4` |
| `tests/runtime/test_replay.py` | `8c9ddff48fed180802dca9b8c4e227ec77ce3443` |
| `tests/runtime/test_signal_quality.py` | `97dccb133749c62fd389c07f6f90203ae4b83aae` |
| `tests/runtime/test_signal_quality_ffmpeg.py` | `2e3e6b6dbd3fb33496502f21e01bcd008de4027a` |

## Important boundaries and required next evidence

- These are **source-matched local Python tests**, not GitHub CI or a
  Docker image/stack execution. The current demo and Operator TS/PWA were
  not executed in this session.
- No PANNs checkpoint was available. The exact selected model cannot
  yet be tested end-to-end on these local inputs.
- The RTSP camera worker and four-source supervision still require
  tests, including `NO_SIGNAL` timestamps, progress isolation and
  restart/recovery.
- The `PARTIAL_SIGNAL` → `INCOMPLETE_SIGNAL` demo semantic adjustment
  was code-reviewed but not yet covered by a full demo-server import/E2E
  test. Its source modification does not affect the nine Python test
  blobs listed above.
- Real near-silence/AAC residue and environment false alarms per
  source-hour remain open under issue #53.
- No controlled benchmark, threshold, model, MQTT acceptance or field
  certification is changed or authorized by these lab results.

### Follow-up integrity checks in the same session

- The same 18-test source-matched subset was rerun **twice** with identical PASS
  outcomes, no errors or skips.
- Pure synthetic 192,000-sample PCM quality inspection (32 kHz, 6 seconds)
  measured median ~12 ms per call for exact-zero, one-LSB, single-nonzero
  and nonfinite controls. These local timing samples are **not** hardware
  certification or throughput SLO evidence.
- Two additional fake-RTSP worker tests were committed in
  `tests/emulator/test_signal_quality_rtsp.py`; **NOT EXECUTED** here.
- Seven additional demo-v2 decision tests were committed in
  `tests/runtime/test_demo_signal_policy.py`; **NOT EXECUTED** here.
- No real PANNs checkpoint, Docker camera worker, Operator browser test or
  external field benchmark was available. The gate remains open.

**Decision: HOLD / DRAFT / NO MERGE.** Run the full checkout, Docker, PANNs
and RTSP acceptance before deciding whether this PR is eligible to merge.
