# RTSP stability — human local validation

**PROCEDURE WRITTEN / NOT_EXECUTED.** Commands below are for the human team.
Implementation ran no tests, builds, Docker, CI or real model inference.
Work from the repository root and preserve pre-hotfix evidence.

## Update the affected services

```bash
git fetch origin
git switch feat/echo-operator-platform-20261026
git pull --ff-only
docker compose --env-file operator/.env -f compose.operator.yaml up -d --no-deps --build --force-recreate echo-rtsp-worker gateway
docker compose --env-file operator/.env -f compose.operator.yaml ps -a
```

Keep the working broker, DB, MediaMTX and emulator running. Gateway rebuild
includes the monitor. Do not use down -v, enable operational acceptance or retune
thresholds/checkpoints to make a source turn green. On the older compose.mvp.yaml
stack, use its live profile and rebuild that worker separately; the frozen demo
page lacks this new Operator diagnostic panel. Avoid duplicate lab stacks when
measuring resources. Required artifact/model/secret preparation is in RUNBOOK.md.

## Capture diagnostic evidence

```bash
docker compose --env-file operator/.env -f compose.operator.yaml logs --tail=150 echo-rtsp-worker
docker compose --env-file operator/.env -f compose.operator.yaml logs --tail=100 rtsp-server vmt-camera-emulator
docker compose --env-file operator/.env -f compose.operator.yaml exec -T echo-rtsp-worker cat /workspace/artifacts/live-monitor/VMT-CAM-003.json
docker compose --env-file operator/.env -f compose.operator.yaml exec -T echo-rtsp-worker ffmpeg -version
docker stats --no-stream
```

Record SHA, image IDs, actual FFmpeg version, elapsed observation time, CPU/RAM
and process/PID limits. Logs emit rtsp_session_end and rtsp_retry_scheduled.
New snapshots contain updated_at and diagnostics.worker_instance_id; absence
means the old worker/image is still running. Worker restart resets its local
attempt counters; the instance ID distinguishes this from emulator generation.
Do not share secrets from unrelated services' logs.

Open http://localhost:8090 and select each source. Expand **Diagnóstico RTSP por
fuente**. Capture multiple snapshots separated by 30–60s for every source.
Counters must increase; heartbeat or MQTT ONLINE alone is insufficient. Record
per-session/cumulative windows, last inference age, phase/phase age, camera/worker
generations, current/last exit, stop/retry reason, queue depth/capacity and stderr.

## Required observations — no PASS prefilled

1. All four sources produce complete windows and real scores/envelopes. CAM-003
   must progress past zero. Compare resource use with previews off and selected
   HLS playback on; record extra reader load.
2. Take CAM-003 offline from the authenticated UI. Other counters must continue.
   Inspect exit/retry reason and bounded backoff, then bring it online. Allow
   current backoff plus window/startup/inference time; no recovery SLA is assumed.
3. Restart CAM-003/change scenario. New worker session/attempt must not reuse old
   temporal state. Emulator generation remains independent. Inspect diagnostic
   lifecycle receipts and confirm no accepted operational alert/push.
4. Observe delay growth on repeated zero-window failures. Reset requires at least
   three windows and 30s of useful session duration. Record exact interruption
   and recovery timestamps; avoid artificial high-frequency manual restart loops.
5. On recurrence, inspect stderr/exit before attributing a cause. Unsupported
   option, path/access, socket timeout, resource/thread or codec errors need
   their own evidence. None automatically establishes a model failure.
6. Verify reconnect heartbeats do not freshen old scores, and previous generation
   waveform/scores are not shown as live. Worker phase and PCM age must stay useful
   while waiting for the shared scorer.
7. In a separately human-approved local overload/stall experiment, verify finite
   queues/processes and explicit PCM_QUEUE_OVERFLOW or RTSP_IDLE_TIMEOUT. Missing
   audio must not be silently stitched. Recurring overflow fails the capacity gate.
8. Gracefully stop/start the worker. Verify decoder termination/reap, new instance
   ID and no accumulating FFmpeg/read threads. Do not kill unrelated host processes
   or change PID/descriptor limits before recording their current values.

If needed, repeat the team's independent 12s decoder comparison inside the
worker container with the audio-only options and without credentials in shared
commands/logs. It adds another reader and changes load. It cannot certify the
four-source operating envelope by itself.

## Written regressions — human execution only

After rebuilding, use local images, not GitHub Actions:

```bash
docker compose --env-file operator/.env -f compose.operator.yaml exec -T echo-rtsp-worker python -m unittest discover -s tests/emulator -p 'test_rtsp_supervision.py' -v
docker compose --env-file operator/.env -f compose.operator.yaml exec -e ECHO_OPERATOR_TEST_ALLOWED=true gateway npm test
```

Python cases use fake processes/scorer, no real model weights. Gateway suite
includes DB/API cases: use a disposable/local stack with a backup. Skips are
not passes. Real audio/video/MQTT/push/visual acceptance remains separate.

## Record the outcome

Retain source/session/instance IDs, timestamps and relevant acceptance rows.
If CAM-003 still fails, provide redacted stderr, current_exit_code/last_exit_code,
reconnect_reason, phase, queue and resource evidence. If it recovers, retain
before/after data and observation duration. One recovery does not certify
long-run stability or N-source capacity.

PR #57 stays draft and dependent on #56. No scientific/acceptance/MQTT contract
changes or enabled operational alerts. Pending human review the state remains
IMPLEMENTED / NOT_EXECUTED / AWAITING_HUMAN_VALIDATION.
