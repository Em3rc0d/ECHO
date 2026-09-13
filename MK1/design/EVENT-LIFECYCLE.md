# Event Lifecycle — MK1

```text
Audio Window
   |
   v
RAW_INFERENCE
   |
 threshold / calibration
   v
CANDIDATE_EVENT
   |
 temporal confirmation + merge
   v
CONFIRMED_EVENT
   |
 alert policy / routing
   +--> EVENT STORE
   +--> MQTT
   +--> ALERT projection
```

## RAW_INFERENCE

Representa scores de una ventana. Puede contener múltiples labels y no tiene `severity` operacional obligatoria.

## CANDIDATE_EVENT

Estado interno keyed por `(source_id, event_type)`. Acumula evidencia, first_seen, last_seen, peak score y número de ventanas.

## CONFIRMED_EVENT

Tiene `event_id`, intervalos temporales, confidence agregada, source, model version y event-engine version. Es idempotente a nivel lógico.

## ALERT

No toda detección debe alertar. `ALERT` es una proyección de policy y puede añadir severity/routing. Cambiar policy de alertas no requiere reentrenar el modelo.