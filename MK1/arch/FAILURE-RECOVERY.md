# MK1 Failure and Recovery

**Status:** `FROZEN_BEHAVIORAL_POLICY / NUMERIC RETRIES EMPIRICAL`

## Source failures

Connection refused, auth failure, no audio, decode error, stall or reboot transition source health and trigger bounded reconnect/backoff where appropriate. Permanent auth/config errors should not retry aggressively forever.

## Stream generation

Reconnect increments generation; old queued/in-flight results are rejected if they would mutate current EventEngine state.

## Inference failures

One invalid window/model exception is recorded and isolated. Repeated model failures degrade service health; they do not fabricate no-target results.

## Overload

Queue saturation is observable. Offline mode waits; live mode applies configured freshness/drop policy. Dropped/stale window counts are evidence for capacity tests.

## Broker failures

Publisher reports unavailable/degraded. MK1 may use bounded retry; it cannot block inference indefinitely. If delivery durability requirements exceed this, MK2 evaluates outbox/durable stream semantics.

## Persistence failures

Failure to store results is explicit. Tests define whether publish may proceed when store fails; no silent divergence between claimed audit trail and actual delivery.

## Process restart

Candidate EventEngine state may reset in MK1 unless persistence is explicitly implemented. This limitation is documented. Stable event IDs/idempotency address transport duplicates but do not imply state recovery.

## Recovery tests

Source disconnect, wrong credentials, decoder kill, queue overload, model exception, broker stop/restart and application restart.

## Invalidation

Final retry/backoff/recovery guarantees become MK2 SLO-backed policy after measurements.