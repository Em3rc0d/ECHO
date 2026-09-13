# Event Engine — MK1

## Responsabilidad

Convertir inferencias ruidosas por ventana en eventos temporales estables.

## Máquina candidata

`IDLE -> ACCUMULATING -> CONFIRMED -> COOLDOWN -> IDLE`.

## Parámetros versionados por clase

- enter threshold;
- exit threshold/hysteresis;
- `min_positive_windows` o duración mínima;
- max gap tolerado;
- merge window;
- cooldown/rearm;
- confidence aggregation.

## No congelar números sin datos

Ejemplos como `0.85`, `2 ventanas` o `10 s cooldown` son placeholders históricos; MK1 debe calibrarlos en validation data y luego verificar en holdout.

## Deduplicación

`event_id` identifica una ocurrencia consolidada. Reintentos de transporte no crean un nuevo evento. Eventos cercanos pueden fusionarse sólo si la regla temporal de la clase lo permite.

## Simultaneidad

El estado se mantiene por `(source_id,event_type)`, permitiendo múltiples clases simultáneas y evitando que un horn bloquee un glass break.