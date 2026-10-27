# RTSP worker stability hotfix — PR #57

Date: 2026-10-26 (America/Lima).
**IMPLEMENTED / NOT_EXECUTED / AWAITING_HUMAN_VALIDATION**.
Base: 1d565f065527c200358a29a7c9432a32bf105d7a, stacked on PR #56.
No main changes, merge, Docker/build/test/CI execution or certificate.

## Evidence and diagnosis

The human team reported the following; this agent did not reproduce the run.

| Source | State | Worker generation | Complete windows |
|---|---|---:|---:|
| CAM-001 | ONLINE | 3 | 161 |
| CAM-002 | ONLINE | 1 | 178 |
| CAM-003 | RECONNECTING / FFmpeg exit 1 | 109 | 0 |
| CAM-004 | ONLINE | 1 | 178 |

A separate FFmpeg process inside the worker container decoded 12s from CAM-003.
These observations do not establish a model failure or a specific connection
limit. **Root cause remains UNKNOWN** pending stderr/resource evidence.

Static inspection identified concrete defects and risks:

1. stderr=DEVNULL erased the primary failure evidence.
2. Each source's thread both read PCM and waited for/scored with the global model
   lock. While waiting, FFmpeg stdout was not drained, causing pipe backpressure.
3. Unbuffered reads can split 4-byte float frames; direct frombuffer could fail.
   This is a structural defect, not a proven explanation of repeated exit 1.
4. An exception could leave one camera thread dead while main kept sleeping.
5. No transport watchdog, exponential backoff, graceful stop propagation or
   inference-independent heartbeat existed.
6. RTSP paths were derived from camera IDs instead of the configured rtsp_path.
7. Decoder/filter threading and video negotiation were not explicitly constrained.

## MediaMTX and emulator inspection

Local MediaMTX configs have no maxReaders override. Upstream v1.21.3 defaults to
maxReaders=0 (no configured per-path reader cap), with 10s read/write timeouts.
That does not rule out descriptor, PID/thread, memory, CPU or host/network limits.

The emulator creates one publisher per distinct path and has no per-reader
admission rule. Its ONLINE state is timer/process based, not decoded audio
health. Automatic encoder/filter threads plus shared container resources are
possible contributors, not selected causes. Publishers, fixtures, codecs and
MediaMTX config remain unchanged. Browser HLS readers add load during validation.
No connection limit was raised to disguise an unknown failure.

## Implementation decisions and files

ADR-002 closes these choices before implementation. The hotfix changes diagnostic
transport/support code on the #57 branch; it does not modify the #56 branch.

* scripts/emulator/rtsp_process.py: per-source process, continuously drained PCM
  and stderr, finite queue (~12s), frame alignment, watchdog, redaction and
  terminate/wait/kill/reap. Stdout is coalesced into fixed aligned chunks, so
  short reads do not accidentally shrink queue duration. No PCM goes to disk.
* Stderr: at most 16 lines of 600 characters, partial-line cap 4096 bytes; omit
  oversized lines. Redact URLs, configured URI credentials and credential-like
  fields. Do not serialize raw commands or exception messages.
* FFmpeg: TCP, audio-only RTSP, input timeout=10000000us, default decoder/filter
  threads=1. PANNs threading/weights and scientific thresholds are unchanged.
* Coordinator: 2/4/8/16/30s interruptible backoff. Reset only after at least three
  complete windows AND a 30s session. Startup is staggered 0.25s/source.
* Shared scorer stays serialized behind an interruptible FIFO gate. RTSP draining
  continues while inference waits. Overflow explicitly ends that session instead
  of silently dropping/stitching samples; retry owns a fresh temporal engine.
* Process exit, idle timeout, overflow, PCM read/truncation, spawn/source errors
  and shutdown have distinct reasons. Cleanup must complete before replacement;
  unreaped children remain REAPING. Unexpected coordinator errors are supervised.
* Existing close_session closes diagnostic occurrences at the last analyzed
  boundary. Late scores from explicitly aborted sessions are not ingested.
  No accepted MQTT target publication is introduced.
* Main publishes heartbeat independently of scoring. at remains last inference;
  updated_at is heartbeat. Worker-instance ID, per-source attempt generation and
  emulator generation stay separate. Reconnect clears stale score/envelope data.
* Gateway/monitor: bounded presentation adapter and per-source diagnostic panel
  expose phase/age, process/exit, duration/windows, retry reason/schedule, queue,
  PCM age, wait/inference times, cleanup and redacted stderr. Fresh heartbeats
  never turn stale inference into live scores.

The complete-window generator's AST is unchanged: same 6s window / 1s hop, no
padding. Models, checkpoints, thresholds, CERT-ECHO-000, acceptance profiles and
certified MQTT schemas/publishers are unchanged. All RTSP output remains lab
only. The operational acceptance list remains empty.

## Written regressions and static review

* tests/emulator/test_rtsp_supervision.py: 15 fake-process/source definitions for
  pipe draining, bounded redaction, split frames, overflow, timeout, termination,
  kill/reap, unreaped children, backoff, FIFO/cancellation, source recovery,
  configured URI mapping, source isolation and heartbeat/inference separation.
* operator/gateway/test/worker-diagnostics.test.ts: 3 adapter definitions for
  heartbeat/staleness, legacy/future snapshots and safe bounded diagnostics.
* Static Python AST parsing (no application imports/execution), AST comparison
  of window generation, TypeScript no-emit analysis and Git whitespace review.

No regression was executed. No Docker/build/CI, real model inference, benchmark
or browser validation was performed. See operator/RTSP-VALIDATION.md for local
commands and required evidence. Stability/capacity/PASS are not claimed.

## Limits and follow-up

Persistent PCM_QUEUE_OVERFLOW is failed throughput/continuity, not success.
Measure load/scorer latency before changing resource policy. Bigger queues cannot
certify capacity. Capture is concurrent; model inference remains serialized.

A scorer call that never returns cannot be safely killed by a Python thread.
Transport termination is still requested and phase age exposed, but full recovery
may require container supervision. An OS-unreapable process remains an explicit
external failure. Window timestamps use the worker clock, not certified RTSP PTS.
Review remaining log contents before sharing them publicly.

## Primary references inspected

* https://github.com/FFmpeg/FFmpeg/blob/n5.1.6/libavformat/rtsp.c — audio-only and
  socket timeout options in the Debian-bookworm FFmpeg family. Actual binary
  version/options remain a local validation gate, not a claim of an executed build.
* https://ffmpeg.org/ffmpeg-protocols.html — RTSP/TCP and timeout units.
* https://github.com/bluenviron/mediamtx/blob/v1.21.3/mediamtx.yml — defaults.
* Repository worker/emulator, Dockerfile, Compose and configuration source.
