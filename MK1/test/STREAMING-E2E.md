# Streaming E2E Tests — MK1

## E2E-01 nominal
Source produce audio -> confirmed event llega a subscriber con mismo `source_id`.

## E2E-02 disconnect
Cortar stream, observar state/reconnect, confirmar ausencia de eventos fabricados durante gap.

## E2E-03 jitter/stall
Inyectar pausas y verificar buffer acotado/telemetry.

## E2E-04 broker unavailable
El pipeline de audio sigue controlado; publishing failure es visible y retry no crea memoria infinita.

## E2E-05 duplicate delivery
Forzar redelivery QoS1 y validar idempotencia por `event_id`.

## E2E-06 multi-source replay
N fuentes mantienen identidad y fairness; ningún event mezcla ventanas.