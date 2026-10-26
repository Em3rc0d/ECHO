# ECHO Operator · experimental MK1 platform

**IMPLEMENTED / NOT_EXECUTED / AWAITING_HUMAN_VALIDATION**

An isolated acoustic operations PWA on top of PR #56. The selected scorer,
Temporal Event Engine, schemas, certificates, frozen professor demo and `main`
are not replaced. No runtime, Docker build, test suite, browser check, benchmark
or deployment was executed during implementation. Source-level TypeScript
analysis is reported separately in the handoff.

## Boundaries

* Source flow: VMT RTSP → existing real scorer → atomic worker snapshots →
  read-only gateway adapter → PostgreSQL diagnostic history + SSE → PWA.
* Event flow: `echo/events` QoS1 → strict versioned schema → lifecycle receipts →
  PostgreSQL occurrence → authorized API/SSE → PWA.
* Operational push: only an independently authorized upstream acceptance profile
  AND matching upstream evidence can create alerts and transactional push jobs.
  **The shipped acceptance profile list is empty.** Current RTSP diagnostics and
  existing controlled demo MQTT messages do not send operational push.
* Lab push: authenticated explicit test route, optional, disabled by default and
  always disabled in production. It tests delivery, not acoustic acceptance.
* Three active classes only: GLASS_SHATTER, SIREN, VEHICLE_HORN. A high score does
  not prove an incident, and temporal CONFIRMED does not mean field acceptance.

See [Docker runbook](RUNBOOK.md), [API contract](API.md),
[validation matrix](../MK1/test/operator/ACCEPTANCE.md),
[architecture ADR](../MK1/arch/operator/ADR-001-OPERATOR.md) and
[design specification](../MK1/design/operator/DESIGN.md).

## Components

| Component | Responsibility |
|---|---|
| gateway/src/mqtt.ts | QoS1 transaction-before-ack, source telemetry, emulator control |
| gateway/src/ingest.ts | Versioned event validation, immutable identity, monotonic lifecycle, routing |
| gateway/src/live.ts | Bounded read-only diagnostics adapter, no RTSP credentials in API |
| gateway/src/server.ts | Session/site authorization, REST/SSE, authenticated HLS proxy |
| gateway/src/push.ts | VAPID, transactional outbox, TTL, retries, provider result |
| db/migrations | Hashed, locked, transactional schema migrations |
| web/src | Responsive dark command center, real envelope/scores, camera control, history |
| web/public | Installable manifest, icons, safe offline surface, push/deep links |
| docker | Local reverse proxy, optional HTTPS VPS proxy, bounded private broker |

No map, VIGIA, identity recognition, speech transcription, new model training or
Android native application. No mandatory paid service. No capacity certification.

Source registration does not dynamically configure the inherited RTSP worker.
Adding ingestion beyond the four lab cameras requires an explicit camera config,
credentials review and per-source acceptance/measurement work.
