# Human acceptance matrix — NOT_EXECUTED

Record date, Git SHA, artifact hashes, OS/Docker/browser/device, exact commands,
expected/observed results, logs/screenshots and PASS/FAIL/BLOCKED for every case.
Blank cells and skipped tests are not passes. Preserve #53 as a separate gate.

| ID | Scenario | Expected behavior | Status |
|---|---|---|---|
| O01 | First local build/start with real artifact cache | Migration/seed complete; admin session; four registered cameras | NOT_EXECUTED |
| O02 | Missing checkpoint/fixture/secrets | Explicit failure; no invented model/score or hidden download/billing fallback | NOT_EXECUTED |
| O03 | Each of four real RTSP scenarios | Real PCM envelope/scores/window times change; LAB label visible | NOT_EXECUTED |
| O04 | Change scenario from UI | Broker ACK distinct from camera telemetry; camera generation changes | NOT_EXECUTED |
| O05 | Offline → online → restart each source | State transitions, stale indication, independent new worker session | NOT_EXECUTED |
| O06 | Open selected HLS video/audio + four optional previews | User-controlled audio; codec works; bounded players; no frame-sync claim | NOT_EXECUTED |
| O07 | CONFIRMED duplicated, CLOSED duplicated | One event occurrence, two receipts, no duplicate alert/outbox | NOT_EXECUTED |
| O08 | CLOSED before CONFIRMED; forged identity | CLOSED never reopens; identity conflict quarantined | NOT_EXECUTED |
| O09 | Wrong schema/version/class/site; oversized payload | Rejected hash/reason recorded; no acoustic acceptance | NOT_EXECUTED |
| O10 | RTSP candidates and controlled MQTT with score=1 | No operational alert or push with empty approved profiles | NOT_EXECUTED |
| O11 | Broker outage and restart during event ingestion | Pending QoS1 redelivery after DB commit boundary; UI transport state | NOT_EXECUTED |
| O12 | DB outage during MQTT ingest | No PUBACK for storage failure; supervised process restart/redelivery | NOT_EXECUTED |
| O13 | SSE interrupted/reconnected | Fresh snapshot/history; no duplicated occurrence; stale values labeled | NOT_EXECUTED |
| O14 | Viewer, operator, admin, second site, disabled/expired account | 401/403/404 boundaries across REST, SSE, HLS, controls and events | NOT_EXECUTED |
| O15 | Cross-origin POST, invalid fields, arbitrary media path/push URL | Mutation denied; HLS/SSRF allowlists enforced | NOT_EXECUTED |
| O16 | Search, filters, UTC dates, pagination, event deep link | Accessible scoped history, preserved original receipts | NOT_EXECUTED |
| O17 | Authorized accepted upstream fixture in disposable reviewed test config | One alert, ACK then resolve, audit trail; acoustic lifecycle unchanged | NOT_EXECUTED / PROFILE_GATE |
| O18 | Mobile PWA installation on approved HTTPS origin | Manifest/icons/install/launch; no operational data in cache | NOT_EXECUTED |
| O19 | Push granted/denied/unavailable/expired subscription | Clear UI state, ownership retained, 404/410 cleanup | NOT_EXECUTED |
| O20 | Explicit LAB notification, tap when closed/open | LAB label; deep link works; no real alert fabricated | NOT_EXECUTED |
| O21 | NODE_ENV=production with ENABLE_LAB_PUSH=true | Lab API forbidden and queued lab deliveries suppressed | NOT_EXECUTED |
| O22 | Burst/retry/429/5xx/TTL/crash-after-send | Finite retry/rate budget; expired jobs suppressed; tag dedup observed | NOT_EXECUTED |
| O23 | Account logout/disable/site access removed | Session revoked, SSE closed, unauthorized push suppressed | NOT_EXECUTED |
| O24 | Backup → isolated DB restore + image rollback | Receipt/audit/membership/outbox integrity; VAPID keys preserved | NOT_EXECUTED |
| O25 | 320/390/768/1440 widths; 200%/400% zoom | No loss of controls; useful mobile hierarchy; screenshots | NOT_EXECUTED |
| O26 | Tab/Shift+Tab/Enter/Escape, screen reader, reduced motion | Focus/labels/status usable; no inaccessible essential control | NOT_EXECUTED |
| O27 | Long run, stalled RTSP, CPU saturation, queue exhaustion | Measured lag/RAM/CPU, explicit stale/overload; no inflated capacity | NOT_EXECUTED |
| O28 | Original professor demo and schema/certificate review | Frozen baseline unchanged; no new PASS or MK2 unlock | NOT_EXECUTED |
| O29 | MediaMTX master cookieCheck 302, audio/video child playlists, init and segments | Gateway handles only the expected internal redirect, preserves session query; actual HLS video and audible audio work through authenticated routes | NOT_EXECUTED |
| O30 | External/cross-camera/loop/query-changing redirect; forged or expired media session; disabled or out-of-site source | Unsafe redirects blocked before follow-up; no cookies/Operator credentials upstream; no source access bypass; request logs omit session query | NOT_EXECUTED |
| O31 | Four-source run including reported CAM-003 zero-window failure | Counters actually advance on all four; capture duration, stderr/exit, phase, queue and CPU/RAM/PID evidence; no model-cause assumption | NOT_EXECUTED |
| O32 | CAM-003 offline/online/restart while other sources process | Independent progress and sessions, bounded backoff, complete process/reader cleanup, no stale scores relabeled live | NOT_EXECUTED |
| O33 | Local stop/stall/overload and thread/scorer failure regressions | Explicit reasons and bounded resources; no PCM stitching; heartbeat separated from inference; no accepted alerts | NOT_EXECUTED |

Written automated cases: `operator/gateway/test/contracts.test.ts` and
`integration.test.ts`. Human command is in operator/RUNBOOK.md. Integration
requires ECHO_OPERATOR_TEST_ALLOWED=true and a disposable running stack.

PR #57 review regression cases are also written in
`operator/gateway/test/hls.test.ts` (seven scripted test cases, NOT_EXECUTED).
These source-level fixtures do not establish actual MediaMTX/browser playback.

RTSP stability regressions: `tests/emulator/test_rtsp_supervision.py` (15 fake
process/source definitions) and `operator/gateway/test/worker-diagnostics.test.ts`
(3 presentation definitions), all NOT_EXECUTED. Human procedures and evidence
requirements are in `operator/RTSP-VALIDATION.md`. There are now 33 manual rows;
none is prefilled as successful by the implementation agent.

For O17 do not edit certified acoustic behavior. Use a separately reviewed
test-only acceptance profile/fixture in a disposable deployment; retain proof
that the shipped/default/production profile list stays empty. This test cannot
close #53 or authorize real field notifications.
