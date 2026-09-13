# MK2 SLO Catalog

**Status:** `METRICS_DEFINED / TARGET_VALUES_PENDING`

## ML/event SLO candidates

`event_recall[class]`, `miss_rate[class]`, `false_alarms_per_source_hour[class]`, aggregate false-alert burden, duplicate/fragmentation rate and calibration error.

## Latency SLO candidates

`source_to_window_lag`, `inference_latency`, `confirmation_latency`, `publish_latency`, `end_to_end_alert_latency` with p50/p95/p99 as appropriate.

## Capacity SLO candidates

Supported source count at declared audio cadence/model/hardware, queue lag ceiling, maximum sustained drop rate, CPU/GPU/RAM/thermal headroom.

## Availability SLO candidates

Healthy-source processing availability, broker publishing availability, service process uptime/recovery time and source reconnection objectives.

## Data/model governance objectives

Reproducible model release, complete artifact provenance, regression pass and rollback readiness are release gates rather than percentages when binary compliance is clearer.

## Privacy/security objectives

No secret leakage, default no-audio retention, authorized field data only, dependency/artifact provenance complete.

## Profiles

Development/lab and production may have different SLO profiles. Claims always name the profile/hardware/model/site assumptions.

## Pending

Numerical values are not filled until MK1 evidence exists; placeholders must be explicitly `TARGET_TBD`, never zero/100% defaults.