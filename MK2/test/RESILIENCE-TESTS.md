# MK2 Resilience Tests

**Status:** `PROTOCOL_SPECIFIED`

## Source faults

Disconnect, auth failure, stall, reboot, codec interruption and reconnect storms while other sources continue. Verify generation change rejects stale work.

## Worker/runtime faults

Kill inference worker, force exception/slowdown, exhaust a bounded queue and restart service. Verify recovery/health and no unbounded replay of stale windows.

## Broker/store faults

Stop/restart/partition broker; make event store unavailable/slow/read-only as applicable. Verify chosen durability/outbox semantics, stable event IDs and explicit degradation.

## Host/resource faults

High CPU/memory pressure, disk pressure, accelerator loss where supported and time-sync disturbance. Verify defined fail/degrade behavior.

## Recovery metrics

Detection interruption by unaffected source, recovery time, lost/duplicate events, queue cleanup, source-state correctness and SLO error-budget impact.

## Pass

System returns to a known healthy state without manual data surgery for tested recoverable faults, and unrecoverable faults produce actionable health state rather than silent corruption.