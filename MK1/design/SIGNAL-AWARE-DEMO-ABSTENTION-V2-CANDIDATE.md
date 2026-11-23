# ECHO-MVP-001 — Signal-aware demo abstention v2 candidate

**Status:** `DESIGN CANDIDATE / NOT CERTIFIED / DO NOT PROMOTE`  
**Date:** 2026-11-22 (America/Lima)  
**Upstream:** issue #53; `MK1/test/FIELD-AUDIO-ROBUSTNESS-GATE.md`  
**Predecessor:** `demo/DEMO-SCOPE-FREEZE.md`, the certified abstention-v1 baseline

## Why a version boundary is necessary

The frozen `ECHO-DEMO-ABSTENTION-v1` exposes `NO_TARGET` and `UNKNOWN`.
A pre-inference signal-quality correctness fix introduces materially different
states, which cannot silently be added to a frozen v1 contract. The candidate
therefore identifies itself as `ECHO-DEMO-ABSTENTION-v2-candidate`.
It is not active in main and is not certified. The predecessor freeze remains
the currently authorized baseline.

The reopening rationale is the frozen demo's explicit exception for a
correctness defect that materially misrepresents ECHO: exact digital zero
produced a model score and a false internal GLASS_SHATTER candidate.

## Decision-layer state table (external WAV/microphone only)

| Input / internal evidence | v2-candidate state | Meaning |
|---|---|---|
| All complete windows exact digital zero | `NO_SIGNAL` | No usable PCM evidence; no model inference |
| All complete windows invalid/unusable PCM, possibly zero | `INVALID_SIGNAL` | Cannot interpret recording as valid acoustic evidence |
| Mixture of scored and rejected windows, without any target candidate | `INCOMPLETE_SIGNAL` | No target confirmed in analyzed subset; **not** proof for entire recording |
| All windows scored; no temporally confirmed candidate | `NO_TARGET` | No target candidate in the analyzed input, not a field-level guarantee |
| One or more uncalibrated external target candidates | `UNKNOWN` | Diagnostic candidate exists; no accepted target |

Source metadata still carries separate `signal_quality_state` and counts.
`UNASSESSED_NONZERO` means **finite nonzero signal**, not evidence of adequate
microphone gain, absence of clipping, calibrated OOD behavior or good SNR.

For any external state, `publish_target_event=false`; model scores cannot
authorize operational MQTT or notifications.

## Compatibility and acceptance

- Existing governed controlled scenarios and their MQTT event behavior are
  unchanged by this candidate; the new gate is opt-in external audio and
  diagnostic RTSP only.
- The public demo UI must show distinct no-signal/incomplete states and must
  not synthesize model scores when no model inference ran.
- Clients expecting `NO_TARGET|UNKNOWN` must explicitly accept the new
  `version` and enumerants before adopting the candidate.
- The v1 document is not overwritten or retroactively certified as v2.
- No v2 promotion until all unit/FFmpeg checks, full Docker demo-server
  acceptance, baseline scenarios, and human contract review pass.
- v2 does not close environmental false-positive issue #53 or certify field
  operation.

## Stop line

`v2-candidate` stays in the draft PR. Release promotion requires a new
versioned freeze/approval and exact end-to-end evidence; do not claim a
production-compatible API on the strength of isolated unit tests.
