# MK2 / Design

## Dominios congelados

```text
Source
StreamSession
AudioWindow
RawInference
CandidateEvent
ConfirmedEvent
AlertEnvelope
ModelVersion
ConfigVersion
Attestation
```

## Versioning

Cada evento MK2 debe identificar:

```text
schema_version
model_version + artifact hash
threshold_version + hash
event-engine config version + hash
code git sha/release
stream_session_id
```

## Delivery semantics

El sistema debe diseñarse para `at-least-once` en el bus cuando se use QoS 1. El consumidor o publisher/outbox debe utilizar `event_id` para idempotencia.

## Model rollout

Estados candidatos:

```text
REGISTERED
VALIDATED
STAGED
ACTIVE
RETIRED
REJECTED
```

Solo un modelo `VALIDATED` puede promoverse a `ACTIVE`.

## Config rollout

Thresholds y Event Engine config son artefactos separados del modelo. Cambiar un threshold no debe requerir reentrenar; sí requiere nueva versión y revalidación.

## Retention

Default:

```text
event metadata: retained per product policy
continuous audio: not retained
evidence clip: optional, encrypted, bounded TTL, policy-controlled
```

## SLO philosophy

SLOs MK2 se congelan usando evidencia MK1. No se copian los target candidates como resultados.