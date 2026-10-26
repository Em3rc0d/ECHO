# ADR-001 — Isolated ECHO Operator experimental platform

Date: 2026-10-26. Decision: ACCEPTED_FOR_IMPLEMENTATION / NOT_EXECUTED.
Authority: user execution directive; PROJECT-CHARTER.md / CERT-ECHO-000.
Base: PR #56, `1ee59f1add866120387d3fc9a5f9a0abd4ec664a`.

Operator is an isolated MK1 experimental support surface. It does not open MK2,
change scientific contracts, train models, or expand the professor's frozen demo.
The required path is local Docker at $0; VPS configuration is optional and does
not authorize provisioning, spending or deployment.

## Closed implementation decisions

* Fastify/TypeScript gateway, PostgreSQL 17, React/TypeScript/Vite PWA; SSE for
  bounded snapshot streaming, REST for mutations, HLS for selected video/audio.
* Reuse PR #56's scorer and worker without modifying them. A read-only adapter
  consumes atomic worker JSON, strips RTSP URIs and marks diagnostic events LAB.
  Emulator status uses its own generation, separate from worker session/generation.
* MQTT QoS1 durable broker/session; handleMessage acknowledges only after a DB
  transaction. Permanent invalid payloads are quarantined by hash/reason, without
  retaining arbitrary payload/audio. DB errors close the process for redelivery.
* One occurrence per event_id. Lifecycle receipts keyed by event_id + lifecycle;
  CLOSED wins even if received before CONFIRMED. Immutable identity conflicts
  are rejected. Original lifecycle payloads are retained separately.
* No score-derived acceptance. Current worker is LAB_DIAGNOSTIC; echo/events is
  CONTROLLED_OR_UNASSESSED. Operational routing requires an explicitly authorized
  upstream acceptance profile AND matching upstream acceptance evidence. The
  shipped profile list is empty. It is not a calibrated OOD detector.
* Acoustic lifecycle and human NEW/ACKNOWLEDGED/RESOLVED states are independent.
* Site membership on every data/media route. Viewer reads, operator acknowledges
  and runs emulator controls, admin manages registry/users. Server sessions use
  opaque hashed tokens, HttpOnly cookies, expiration and same-origin mutation
  checks. No credentials are stored by the service worker.
* Push uses a transactional outbox, bounded retries, TTL, per-user minute budget,
  endpoint allowlist, expired-subscription cleanup and provider acceptance logs.
  Provider acceptance never claims device receipt. Lab push is a separate,
  authenticated, explicitly enabled route and is forbidden in production.
* No raw audio storage. Selected HLS playback requires a user gesture; up to four
  muted previews are opt-in. HLS has a playback delay and is not frame-synchronized
  with inference. Both freshness and measured snapshot age remain visible.

## Capacity and recovery

One gateway replica; no claim of 100 cameras. Maximum 50 SSE clients, 256 KiB
MQTT packets, one DB ingestion transaction at a time, bounded live snapshot size,
64 envelope bins, maximum 1000 registered sources, paginated history, four
optional previews and one selected player. The inherited worker serializes model
inference; CPU fairness/lag are empirical gates. DB/outbox durable, telemetry
ephemeral. SSE reconnect re-fetches current state; persisted history is authoritative.

## Open empirical/external gates

Runtime, Docker build, migration/restore, browser layout, mobile installation,
push delivery, codec playback, MQTT reconnect/order, capacity, accessibility and
security tests are NOT_EXECUTED. Model/domain robustness #53 remains OPEN.
Production acceptance profiles remain empty until independently authorized.

Sources consulted (primary): https://github.com/mqttjs/MQTT.js,
https://fastify.dev/docs/latest/Reference/Reply/,
https://github.com/web-push-libs/web-push,
https://mediamtx.org/docs/features/expose-the-server-in-a-subfolder.

SSE frames are capped at 2 MiB and slow clients are disconnected; diagnostic
transition summaries in snapshots are bounded separately from persisted receipts.
