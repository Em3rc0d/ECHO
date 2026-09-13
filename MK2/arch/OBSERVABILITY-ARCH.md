# Observability Architecture — MK2

## Signals

### Metrics
Per-source health, buffer depth, RTF, latency histograms, errors, reconnects, events, publishes, resource utilization.

### Logs
Structured, correlated por `source_id/event_id/build_id`; secrets redacted.

### Traces
Opcional cuando componentes se separen: capture/window -> inference -> event -> publish.

## Dashboards target

- fleet/source health;
- latency/backlog;
- event volume by class/source;
- model/version distribution;
- false-positive review feed cuando exista ground truth;
- broker/delivery health.

## Alerts de sistema

Separar alertas operacionales de alertas acústicas para evitar loops/confusión.