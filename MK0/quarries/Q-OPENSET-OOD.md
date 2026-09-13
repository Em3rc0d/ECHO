# Quarry — Open Set / OOD

`OTHER` es una clase operacional, no una solución matemática a open-set recognition.

## Opciones a investigar

- threshold por clase;
- temperature scaling / calibration;
- energy/max-probability rejection;
- embedding distance a prototipos;
- hard-negative mining iterativo;
- abstention policy.

## Riesgo

Un threshold global puede castigar clases con distribución de scores distinta. La política debe medirse por clase y condición.

## Resultado esperado

Para MK1, una política de abstención simple y explicable puede ser preferible a un algoritmo OOD complejo si reduce false alarms en holdout real.