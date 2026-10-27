# PR #57 — HLS review correction

Date: 2026-10-26 (America/Lima).
Status: IMPLEMENTED / STATICALLY_REVIEWED / TESTS_NOT_EXECUTED.
Review: https://github.com/Em3rc0d/ECHO/pull/57#pullrequestreview-5660875348
Original implementation: 899f2f424ac6f68ae09244ea6acb99aafa29d849.

## Findings and decision

The reviewer correctly identified that `redirect: error` rejects MediaMTX's
cookieCheck 302. Pinned v1.21.3 upstream source also shows the session query
fallback: when cookieCheck is not sent as a cookie, relative child and fragment
URIs carry a `session` UUID. The original query allowlist discarded this UUID,
so following the 302 alone would not complete the playback path.

The fix uses MediaMTX's existing query fallback, not a shared server cookie jar
or a CDN authentication bypass. A small pure transport module validates the
registered camera's flat HLS filename, upstream origin and allowed query values.
It follows only one 302 back to the exact master playlist with only the expected
cookieCheck query addition. It does not relay Operator/browser cookies, upstream
Set-Cookie, authentication headers or redirects to the browser. Child playlists
and segments preserve a validated session UUID. Registry/site/session/enabled
checks remain before transport on every resource. Query strings are excluded
from request logs. Redirect response bodies are discarded, both fetches share
one timeout, and client disconnect aborts the stream.

No MediaMTX version/configuration, ports, PWA player behavior, acoustic model,
certified schema, acceptance policy or deployment was changed. Audio starts
muted and still requires the operator's explicit playback/audio interaction.

## Files and unexecuted regressions

* `operator/gateway/src/hls.ts`: bounded manual handshake and query validation.
* `operator/gateway/src/server.ts`: authorized integration, safe logging and abort.
* `operator/gateway/test/hls.test.ts`: seven scripted cases for 302/session chain,
  relative redirect/query retention, direct status responses, open redirect/SSRF
  and cross-source rejection, loops/unexpected redirects, paths/queries and abort.
* `operator/gateway/test/integration.test.ts`: additional 401/404 media checks
  covering cookieCheck/session queries, site membership and disabled sources.
* API, runbook, acceptance matrix, open gates and handoff updated.

No test file, Docker command, server, browser, build, benchmark or CI was run.
Static TypeScript/whitespace checks are reported separately from runtime tests.
The matrix now has 30 required human scenarios; all remain NOT_EXECUTED.
G03 remains OPEN. The reviewer has not approved runtime playback; no review
thread is marked resolved and no new certification is claimed.

## Primary source evidence inspected

* https://github.com/bluenviron/mediamtx/blob/v1.21.3/internal/servers/hls/http_server.go
  — 302 cookieCheck handshake and request routing.
* https://github.com/bluenviron/mediamtx/blob/v1.21.3/internal/servers/hls/session.go
  — cookie versus query fallback when generating HLS responses.
* https://github.com/bluenviron/mediamtx/blob/v1.21.3/internal/servers/hls/server.go
  — session lookup bound to path and upstream client IP.
* https://mediamtx.org/docs/features/expose-the-server-in-a-subfolder
  — reverse-proxy path and redirect requirements.

No runtime outcome is inferred from reading these sources. Keep PR #57 draft,
dependent on #56, no merge, and with operational acceptance profiles empty.
