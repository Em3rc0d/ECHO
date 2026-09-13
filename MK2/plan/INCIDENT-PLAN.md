# MK2 Incident Plan

**Status:** `SPECIFIED / OPERATOR OWNERSHIP TO ASSIGN`

## Incident classes

Source fleet outage, inference degradation/overload, false-alert spike, missed-event regression, broker/store outage, credential/security incident, privacy/media retention issue, bad model/config release and data/model drift.

## First response

Identify scope/source/release, preserve logs/metrics/config/model IDs, stop unsafe/incorrect automated actions if any, rollback/disable affected component when appropriate and avoid deleting evidence needed for diagnosis within retention policy.

## Severity

Severity should consider affected sources, duration, privacy/security exposure and event-quality impact. Acoustic event severity is different from operational incident severity.

## Runbook inputs

Dashboard/alerts, active release manifest, source health, queue/runtime metrics, broker/store health and recent deployment history.

## Post-incident

Root-cause category, timeline, impact, corrective action, new regression test/risk entry and whether a certificate/model/SLO must be invalidated.

## Security/privacy

Credential exposure triggers revoke/rotate and access/log review. Unauthorized raw-audio retention triggers containment/deletion/review according to policy.

## Validation

Tabletop/fault drills before release for at least broker outage, source outage, bad model release and secret compromise scenario.