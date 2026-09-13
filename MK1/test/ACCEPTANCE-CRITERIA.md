# MK1 Acceptance Criteria

**Status:** `DEFINED / NUMERIC SLOS TO FREEZE FROM EVIDENCE`

## Functional acceptance

Replay -> inference -> EventEngine -> confirmed event -> MQTT -> subscriber/store works under versioned contracts. Multiple replay sources preserve source identity/state. Known target/no-target/unknown cases produce deterministic lifecycle behavior under frozen config.

## Scientific acceptance

Valid group-aware splits, no known leakage, A/B/C result bundles comparable, thresholds chosen on validation, untouched test/field holdout, per-class + operational metrics and documented error analysis.

## Operational acceptance

Queues/buffers bounded; overload visible; source failure isolated; broker failures observable; restart/reconnect behavior documented; runtime profile recorded on declared hardware.

## Delivery acceptance

QoS1 duplicate behavior does not create duplicate logical consumer actions when event_id idempotency is applied. Topic/schema versions validated.

## Privacy/security acceptance

No committed secrets, no plaintext credentials in normal logs, no continuous raw-audio files by default, checkpoint hashes verified, field capture gated by authorization.

## Numeric quality

MK0 intentionally did not invent exact recall/false-alarm/latency thresholds. Early MK1 measurements define candidate SLOs, which are frozen **before final test evaluation**. A candidate failing them is reported as failure rather than moving the line after seeing results.

## Completion

All blocking criteria PASS; camera-specific criteria may remain external only if MK1 certificate scope explicitly excludes real-camera claims.