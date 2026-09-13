# Operations Scenarios — MK2

## S1 — Site local
Varias cámaras/NVR en LAN; ECHO procesa localmente y publica metadata.

## S2 — Edge + central metadata
Cada sitio infiere localmente; central recibe eventos, métricas y model versions.

## S3 — Central inference
Fuentes remotas transmiten audio hacia cluster central. Mayor dependencia de red y superficie de privacidad.

## S4 — Degraded site
Broker/cloud no disponible; detección local continúa según política y eventos pueden persistirse/reintentarse si el delivery design lo requiere.

## S5 — Model rollout
Nueva versión se despliega canary/shadow, compara telemetría y sólo luego reemplaza estable.

La arquitectura final selecciona escenarios explícitos; no intenta resolver todos con la misma complejidad.