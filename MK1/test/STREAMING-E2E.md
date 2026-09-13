# MK1 Streaming End-to-End Tests

**Status:** `SPECIFIED`

## Replay corpus

Construct long streams that include mostly negative background, target occurrences, close repeated events, overlapping classes and high-risk confusers. Preserve event onset/offset ground truth where available.

## E2E trace

For each physical event trace source/window IDs -> raw scores -> EventEngine transitions -> confirmed event ID -> MQTT publication -> subscriber/store record.

## Metrics

False alarms/source-hour, event recall/misses, confirmation and alert latency p50/p95/p99, duplicates/fragmentation, queue lag/drops, broker delivery and source health.

## Negative soak

Long negative replay is mandatory because short balanced clips hide operational false-positive rates.

## Multi-source cases

Concurrent streams with simultaneous targets, one noisy source and one reconnecting source. Verify other sources continue and event state never crosses source ID.

## Overload

Intentionally exceed inference capacity. Memory remains bounded; live-mode stale/drop counters rise; system must not pretend it remained real-time.

## Broker fault

Stop/restart broker; verify publisher health/retry behavior and idempotent consumer after reconnect.

## Result bundle

Event log, inference sample/prediction file, metrics, runtime profile, build/config/model/data hashes and error analysis.