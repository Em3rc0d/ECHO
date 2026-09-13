# Model Governance — MK2

## Model package

Cada modelo incluye model ID/version, checkpoint hash, taxonomy version, preprocessing version, training dataset manifest, metrics report, calibration artifact, license/notices y runtime requirements.

## States

`EXPERIMENTAL -> CANDIDATE -> VALIDATED -> PRODUCTION -> DEPRECATED -> RETIRED`.

## Promotion

Un modelo no pasa a `PRODUCTION` si falla regression suite, field holdout, latency/resource gate o license gate.

## Rollback

La versión anterior permanece disponible durante ventana definida. Thresholds y calibration se versionan junto al modelo; nunca se reutilizan implícitamente.

## Drift

Monitorear cambios en score distributions, class prevalence, hard-negative patterns y source acoustic statistics. Drift alerta revisión; no auto-reentrena sin gate.