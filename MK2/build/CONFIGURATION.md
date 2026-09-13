# Configuration — MK2

## Desired hierarchy

`defaults < site config < source config < deployment overrides < secrets`.

Todos los valores efectivos no secretos se pueden exportar a snapshot para auditoría. Secrets se representan por referencias, nunca por valor.

## Hot reload

Sólo parámetros seguros (p.ej. enable/disable source) pueden recargarse sin restart. Cambios de taxonomy/model/preprocessing requieren rollout versionado para evitar mezclar estados incompatibles.