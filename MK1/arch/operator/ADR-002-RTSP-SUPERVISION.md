# ADR-002 — Per-source RTSP process supervision

Date: 2026-10-26 (America/Lima). IMPLEMENTATION_AUTHORIZED / NOT_EXECUTED.
Base: PR #57 after 1d565f0, still dependent on PR #56. No change to main.

The human team reports CAM-003 reconnecting at generation 109 with zero windows
and FFmpeg exit 1 while the other three sources make progress. An independent
FFmpeg process in the worker container decoded 12s of CAM-003 audio. These are
reported observations, not results reproduced by the implementation agent.
The failure's root cause is UNKNOWN; neither the model nor a connection limit
is established as its cause.

## Decisions closed before implementation

* Supervise one decoder process and independent bounded stdout/stderr drainers
  per source. PCM frame alignment is maintained across arbitrary pipe reads.
  Audio remains memory-only, complete 6s windows / 1s hop, same real scorer.
* Keep model inference serialized for the shared scorer, with a cancellable
  FIFO gate. RTSP draining must continue while another camera owns the scorer.
* A finite PCM queue (default approximately 12s) must not silently lose/stitch
  samples. Queue overflow ends that diagnostic session, records the reason and
  starts a fresh session/Temporal Event Engine after bounded backoff. This is
  observable lost continuity, not a claim to lossless processing under overload.
* Request RTSP audio only over TCP, use FFmpeg's verified `timeout` option, and
  cap decoder/filter threads at 1 by default. Use configured `rtsp_path` rather
  than deriving it from a camera ID. No PANNs threading/weights/threshold change.
* Drain stderr continuously into at most 16 redacted 600-character lines. Drop
  oversized unterminated lines instead of exposing partial credentials. Never
  store/emit raw RTSP URI, subprocess command or unsanitized exception messages.
* An independent transport watchdog stops a stalled decoder. Terminate, bounded
  wait, kill and bounded reap must precede replacement; an unreaped child blocks
  replacement for that source. Other sources keep their own process/state/engine.
* Retry delays are 2/4/8/16/30s by default; only a session with at least three
  windows and 30s of operation resets the failure sequence. Shutdown interrupts
  waits. A worker-instance identifier distinguishes generation counters after
  process restart. Emulator generation remains a separate identity.
* Publish process diagnostics on a heartbeat independently of inference. Keep
  `at` as last inference time and `updated_at` as snapshot heartbeat time. Fresh
  heartbeats must not make old scores appear live. Clear scores on reconnect.
* Close active diagnostic temporal events using the existing close_session
  method on termination, without publishing any accepted MQTT target event.

## Scope and limits

No scientific/acceptance/MQTT contract changes and no operational alerts. This
changes the diagnostic worker on the #57 branch only; #56 remains its dependency.
MediaMTX/emulator configuration and publishers are inspected, not redesigned.
Resource limits, per-path reader counts and publisher restarts still need local
evidence. A hung in-process scorer cannot be forcibly interrupted safely by a
thread; the transport is still stopped/diagnosed, but model-hang recovery remains
a container-supervision limitation, not a fabricated stability guarantee.

All regression tests, Docker/build/CI, model execution and runtime recovery
checks remain NOT_EXECUTED. No capacity or PASS is claimed.
