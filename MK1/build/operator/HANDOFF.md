# ECHO Operator implementation handoff — 2026-10-26

**Status: IMPLEMENTED / NOT_EXECUTED / AWAITING_HUMAN_VALIDATION**
**Visual status: SOURCE_IMPLEMENTED / VISUAL_QA_NOT_EXECUTED**

RTSP follow-up: [hotfix diagnosis and changes](RTSP-STABILITY-HOTFIX.md), with
local instructions in operator/RTSP-VALIDATION.md. The diagnostic worker is now
modified on #57 for process/pipe supervision, backoff and observability; scientific
contracts remain unchanged. Fifteen Python and three gateway regression cases
are written, not executed. The human CAM-003 exit-1 report does not establish
a root cause or successful recovery. The current human matrix has 33 scenarios.

Review follow-up: [HLS correction](HLS-REVIEW-CORRECTION.md) handles the confined
cookieCheck redirect and preserves MediaMTX session queries. Seven additional
HLS test cases and more DB/API media authorization checks are written but
NOT_EXECUTED. HLS added scenarios 29–30; runtime/media gates stay open.

## Delivered behavior

Dedicated MK1 experimental support platform: PostgreSQL migration/seed, MQTT
QoS1 gateway, canonical schema adapter, lifecycle receipt idempotency,
read-only live inference adapter, authenticated site-scoped REST/SSE/HLS,
responsive dark React PWA, selected audiovisual camera monitor, real envelope
and score traces, source controls, history/deep links, alert acknowledgement and
resolution, account/registry administration, Web Push outbox and delivery history.

The existing four-camera RTSP/scorer/TemporalEventEngine implementation is reused.
No scientific thresholds, model weights, canonical schemas, certificates or
frozen professor-demo files were modified. The latest PR #56 source already
included local HLS/control support despite its older PR body; Operator supplies
its own authenticated media/control adapter and reuses the emulator contracts.

## Routing and scientific boundary

RTSP diagnostic snapshots → LAB_DIAGNOSTIC history/SSE; no target publication.
Existing echo/events → CONTROLLED_OR_UNASSESSED unless a separately authorized
upstream profile/evidence pair is present. The shipped profile list is empty.
Operational alert → transactional outbox → enabled/scoped subscription → Web Push
provider result. Lab delivery is separate, explicitly labeled, off by default,
and forced off in production. No score is promoted to a crime/emergency claim.
Severity remains UNASSESSED unless future authorized operational policy exists.

CONFIRMED/CLOSED lifecycle and NEW/ACKNOWLEDGED/RESOLVED human states are separate.
One occurrence retains both original receipt payloads. Closed-first delivery
cannot reopen the occurrence. MQTT.js acknowledgement follows durable ingestion;
DB failure causes supervised restart/redelivery instead of acknowledgement.

## Verification performed / deliberately not performed

* Static TypeScript `tsc --noEmit`: frontend and gateway (including written test
  sources), with source errors corrected. This is type analysis, not app execution.
* Static YAML/JSON parsing and Git whitespace inspection; installed MQTT handler
  source reviewed for transaction-before-PUBACK callback sequencing.
* Dependency lockfiles resolved with npm lifecycle scripts disabled; no model,
  database, server, frontend or Docker runtime was started.
* No unit/integration/E2E tests, Docker build/smoke, browser tests, visual renders,
  benchmark/load tests, deployment, CI execution, certification or merge.
* Written tests: three contract/routing test cases and one DB/API integration
  case. Integration needs an explicitly enabled disposable running Docker stack.

Therefore no runtime PASS, visual polish verification, field acceptance,
production readiness, capacity or device-delivery claim is made.

## Start and review

See `operator/RUNBOOK.md` for artifact prerequisites, secret generation, local
Docker startup, browser/mobile validation, backup/restore, rollback and optional
HTTPS configuration. No VPS or paid resource was created. Default local entry:
`http://localhost:8090`. A phone requires an approved secure HTTPS origin;
localhost on the phone points to the phone itself.

See `operator/API.md`, `MK1/arch/operator/ADR-001-OPERATOR.md`,
`MK1/design/operator/DESIGN.md`, `MK1/test/operator/ACCEPTANCE.md`, and
`MK1/quarries/operator/OPEN-GATES.md` for contracts, visual rules and human
acceptance scenarios and remaining limitations. The source changes implement
ordinary architecture choices; empirical and external gates remain OPEN.

## Git / release boundary

Branch: `feat/echo-operator-platform-20261026`.
Dependency/base: `feat/rtsp-live-monitor-mk1`, PR #56,
`1ee59f1add866120387d3fc9a5f9a0abd4ec664a`.
Main inspected: `05f81f0e4aee051f9cf1c74deb05678a7ae82d65`.
Delivery is a stacked draft PR against the dependency branch, with no merge.
The actual published commit/PR identity is recorded by Git/GitHub, avoiding
self-referential commit hashes inside this document.

Automatic workflow path filters were inspected before publishing; none matches
this change. No workflow files, corpus/data-foundry/schema paths or certified
runtime code are modified. Commit/PR skip markers are additional protection.

## File inventory

- `.dockerignore`
- `.gitignore`
- `CURRENT-STATE.md`
- `MK1/arch/operator/ADR-001-OPERATOR.md`
- `MK1/brainstorming/operator/CONTEXT.md`
- `MK1/design/operator/DESIGN.md`
- `MK1/mining-site/operator/PROVENANCE.md`
- `MK1/plan/operator/IMPLEMENTATION.md`
- `MK1/quarries/operator/OPEN-GATES.md`
- `MK1/test/operator/ACCEPTANCE.md`
- `README.md`
- `REPOSITORY-MAP.md`
- `THIRD_PARTY.md`
- `compose.operator.vps.yaml`
- `compose.operator.yaml`
- `operator/.env.example`
- `operator/API.md`
- `operator/README.md`
- `operator/RUNBOOK.md`
- `operator/config.acceptance.json`
- `operator/db/migrations/001_operator.sql`
- `operator/docker/Caddyfile.local`
- `operator/docker/Caddyfile.vps`
- `operator/docker/Dockerfile`
- `operator/docker/mediamtx.yml`
- `operator/docker/mosquitto.conf`
- `operator/gateway/package-lock.json`
- `operator/gateway/package.json`
- `operator/gateway/src/auth.ts`
- `operator/gateway/src/bootstrap.ts`
- `operator/gateway/src/config.ts`
- `operator/gateway/src/contracts.ts`
- `operator/gateway/src/db.ts`
- `operator/gateway/src/ingest.ts`
- `operator/gateway/src/live.ts`
- `operator/gateway/src/migrate.ts`
- `operator/gateway/src/mqtt.ts`
- `operator/gateway/src/push.ts`
- `operator/gateway/src/server.ts`
- `operator/gateway/test/contracts.test.ts`
- `operator/gateway/test/integration.test.ts`
- `operator/gateway/tsconfig.json`
- `operator/tools/init-secrets.mjs`
- `operator/web/index.html`
- `operator/web/package-lock.json`
- `operator/web/package.json`
- `operator/web/public/icon-192.png`
- `operator/web/public/icon-512.png`
- `operator/web/public/icon.svg`
- `operator/web/public/manifest.webmanifest`
- `operator/web/public/offline.css`
- `operator/web/public/offline.html`
- `operator/web/public/sw.js`
- `operator/web/src/main.tsx`
- `operator/web/src/style.css`
- `operator/web/tsconfig.json`
- `MK1/build/operator/HANDOFF.md` (this handoff)
