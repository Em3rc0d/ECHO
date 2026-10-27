# Operator API v1 — presentation adapter contract

Status: IMPLEMENTED / NOT_EXECUTED. Prefix `/api`; same-origin JSON. This API
does not change `echo.event.v1`. Version 0.1 is experimental, not certified.

Session cookie: opaque 32-byte token, SHA256 stored in PostgreSQL, HttpOnly,
SameSite=Strict, Secure on HTTPS, eight-hour expiry. Every mutation requires
Origin equal to PUBLIC_ORIGIN; rate limits apply. Every data/media request
checks enabled account, valid session and site membership. Viewer reads;
operator also controls lab sources and attends alerts; admin manages accounts
and registry within its site scope. No default unauthenticated control route.

| Method/path | Access | Result |
|---|---|---|
| POST /login | Public + same origin | `{username,password}` → session cookie |
| POST /logout | Session | Deletes current server session |
| GET /me | Session | User, sites, role, push configuration (public VAPID only) |
| GET /snapshot | Session/site | Sources, health, diagnostics, latest 50 events / 100 alerts |
| GET /stream | Session/site | SSE `snapshot` every 2s, reconnect supported; max 50 clients |
| GET /events | Session/site | 50 rows; filters source/type/lifecycle/origin/from/to; offset |
| GET /events/:event | Session/site | Occurrence, original lifecycle receipts, alert and audit |
| POST /alerts/:alert/acknowledge | Operator/site | NEW → ACKNOWLEDGED |
| POST /alerts/:alert/resolve | Operator/site | ACKNOWLEDGED → RESOLVED |
| POST /sources/:source/control | Operator/site/emulated | Existing MQTT control command; broker ACK only |
| GET /media/:source/* | Session/site/enabled | Allowlisted HLS filename proxy, confined cookie-check redirect and validated session query; no RTSP URI exposure |
| GET /health | Session | Database, MQTT, snapshot/client counters |
| GET /push | Session/owner | Own subscription IDs and 30 delivery results; no private keys/endpoints |
| POST /push/subscriptions | Session/owner | Browser PushSubscription JSON; allowlisted provider host |
| DELETE /push/subscriptions | Session/owner | `{endpoint}` disables owned subscription |
| POST /push/lab | Operator, lab mode only | Explicit non-acoustic test message to own subscriptions |
| GET/POST /admin/users | Admin/site | List scoped accounts / create username,password,role,sites |
| PATCH /admin/users/:user | Admin/site | enabled,role,sites; revokes target sessions; no self mutation |
| POST /admin/sources | Admin/site | Register source or update existing name/enabled |
| POST /admin/sites | Admin | Create site and assign current admin |

Dates in API are UTC ISO8601. UI shows local time and retains UTC in event
detail. No score is an incident probability. Offset max 100000; no full-corpus
export is implicit. Input validation errors return 400; unauthenticated 401;
forbidden 403; inaccessible identity 404; invalid human lifecycle transition 409;
capacity/disabled push 503. Database/internal failures expose a generic error.

## MediaMTX v1.21.3 session transport

Every master playlist, child playlist, init file and fragment request requires
the current Operator session plus source/site/enabled checks **before** transport.
The client cannot choose an upstream host or another registered camera path.

The gateway uses `redirect: manual`, permits at most one HTTP 302 only from
`index.m3u8` back to the exact same origin and pathname, and requires its only
query change to be `cookieCheck=1`. Missing Location, loops, other statuses,
credentials, fragments, cross-camera paths, other hosts/ports and query changes
are rejected. The same 20s deadline covers both requests; browser disconnect
aborts the upstream stream. No upstream Location or Set-Cookie is forwarded.

The gateway intentionally sends neither browser cookies, Operator credentials,
nor a cookieCheck cookie upstream. This selects MediaMTX's built-in query-mode
session fallback; MediaMTX adds `session=<UUID>` to the returned relative HLS
URIs. The proxy preserves and validates this parameter for child playlists and
fragments, alongside `_HLS_msn`, `_HLS_part` and `_HLS_skip`. Duplicate/invalid
recognized parameters are rejected; unknown parameters are discarded. No global
cookie jar, shared CDN bypass credential or additional port is introduced.
Request logs omit query strings because upstream HLS session tokens are bearer
secrets. These tokens do not replace Operator authentication/authorization.

This behavior was checked against upstream **source**, not an executing server:
https://github.com/bluenviron/mediamtx/blob/v1.21.3/internal/servers/hls/http_server.go
and `session.go` / `server.go` in the same release. Runtime regression cases are
written but NOT_EXECUTED. An expired upstream session still returns an error;
the operator may need to reopen the player after a fatal media error.

## MQTT mapping and lifecycle

* Input `echo/events`, QoS1; required contract validated against unchanged
  `schemas/event.schema.json` plus the existing provenance.lifecycle convention.
* `CONFIRMED` and `CLOSED` share one event_id; both original payloads are retained.
* One receipt per `(event_id,lifecycle)`, one occurrence per event_id. Same
  identity re-delivery is idempotent; source/site/session/model/threshold/onset
  identity conflict is quarantined. CLOSED cannot be reopened by a late CONFIRMED.
* Source health consumes existing `vmt/cameras/+/status|telemetry` and verifies
  topic/source/site against the registry. Camera and worker generations differ.
* Controls publish the existing set_scenario/set_online/restart payloads to
  `vmt/cameras/<source_id>/control`. `accepted_by_broker=true` does not mean a
  camera executed it. Subsequent telemetry is the observed confirmation.
* Worker snapshot candidates use an explicit LAB_DIAGNOSTIC origin and never
  change the event publisher or scientific policy.

## Operational acceptance bridge (closed by default)

`operator/config.acceptance.json` intentionally contains no approved upstream
profiles. Current MQTT events become CONTROLLED_OR_UNASSESSED. Implementing
Operator has not calibrated a field/OOD acceptance policy.

A **future separately approved** upstream adapter could attach
`provenance.operator_acceptance={accepted:true,profile_id:...}` to the existing
open provenance object, while a reviewed routing entry binds profile_id,
site_id,source_id,model_version,threshold_version. Only both matching conditions
can authorize operational routing. The gateway never evaluates scores to make
this decision. Merely editing routing JSON is not governance approval. No
profile, certificate or upstream acceptance claim was created in this change.

## Push semantics

Transactional DB outbox, unique subscription/event dedup key, 120s expiry, max
three attempts, retry delay 15s, max five recently attempted delivery records
per user/minute, per-provider 10s timeout. 404/410 disables subscription; 429/5xx
or transport errors may retry. Subscription ownership cannot move silently
between users. Site access is rechecked before sending. Provider host allowlist
prevents arbitrary server-side request targets. No hidden push analytics service.

PROVIDER_ACCEPTED != DEVICE_RECEIVED != USER_READ. Crash redelivery is possible;
browser notification tags reduce duplicate presentation. Lab messages have their
own dedup key, explicit label, no acoustic alert, and production suppression.
