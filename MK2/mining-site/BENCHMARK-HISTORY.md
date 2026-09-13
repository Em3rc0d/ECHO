# MK2 Benchmark History

**Status:** `SCHEMA_READY / NO MK2 RESULTS YET`

## Purpose

Maintain longitudinal, comparable evidence across production candidates/releases without overwriting inconvenient regressions.

## Record format

For each benchmark: release/model/config/data-suite/hardware IDs; source count/profile; quality metrics; false alarms/misses; latency/resources; capacity/drop/fairness; date/runtime versions; result bundle URI/hash.

## Comparability flags

Mark `COMPARABLE`, `PARTIAL`, or `NOT_COMPARABLE` based on taxonomy/data suite/hardware/protocol changes. Never draw trend lines across materially different benchmarks without noting the difference.

## Use

Model promotion, capacity planning, SLO revision and cost analysis consume this history. It also shows whether improvements persist across releases rather than one benchmark.

## Raw evidence

Machine-readable reports remain in artifact storage; this Markdown summarizes identities/conclusions once results exist.

## Current state

No MK2 benchmark result is fabricated here. First record is created only after a release candidate runs the frozen protocol.