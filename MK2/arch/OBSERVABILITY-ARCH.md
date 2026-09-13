# MK2 Observability Architecture

**Status:** `DESIGN_SPECIFIED`

## Signals

Metrics for source health, decode, buffers/queues, inference workers, EventEngine, broker/delivery, storage and release/model identity. Structured logs for causal diagnostics. Optional traces correlate a window/event across components without carrying raw audio.

## Golden operational questions

Which sources are online but acoustically silent? Where is latency accumulating? Are drops unfairly concentrated? Did false alerts spike after a model/config release? Is broker delivery failing while detection remains healthy? Which release produced an event?

## Metrics design

Histograms for latency/queue age; counters for drops/reconnects/errors/events; gauges for queue fill/resource use/source state. Avoid high-cardinality event/source details in metric labels beyond bounded dimensions.

## Release correlation

Every service exposes code/model/config/schema version. Dashboards/alerts annotate releases so drift/regression can be associated with change.

## Privacy/security

No raw audio in logs/traces; redact RTSP credentials; protect observability backend because source/site/event metadata may be sensitive.

## Alerting

Health alerts should be symptom/action oriented: source stale, queue SLO violated, worker saturation, broker unavailable, storage errors, model regression signal. Acoustic alerts are product events and remain separate.

## Validation

Fault/load tests must demonstrate expected telemetry before release.