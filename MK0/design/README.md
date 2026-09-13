# MK0 / Design

## Diseño conceptual

ECHO separa cuatro niveles semánticos:

```text
RAW_INFERENCE
    ↓ temporal aggregation / thresholding
CANDIDATE_EVENT
    ↓ confirmation rules
CONFIRMED_EVENT
    ↓ routing/policy
ALERT / PUBSUB
```

Esto evita confundir “el modelo produjo score 0.82” con “ocurrió un evento confirmado”.

## Entidades conceptuales

### Source

Representa un punto de captura, no necesariamente una cámara.

```text
source_id
site_id
kind: ip_camera | microphone | replay
stream_uri_ref
capabilities
tags
status
```

### AudioWindow

```text
window_id
source_id
stream_session_id
start_utc
end_utc
sample_rate
channels
samples/hash
```

### RawInference

```text
window_id
model_version
scores[class]
inference_ms
```

### AcousticEvent

```text
event_id
source_id
event_type
onset_utc
end_utc
confidence_peak
confidence_mean
model_version
threshold_version
provenance
```

### Alert

Es una consecuencia de policy/routing, no la salida directa del modelo.

## Multi-label vs single-label

`DECISION_CANDIDATE`: multi-label con sigmoid, porque sonidos reales pueden coexistir. Debe validarse con disponibilidad de labels y evaluación.

## Unknown/background

ECHO no debe forzar cualquier audio a una clase target. Diseñar explícitamente:

```text
background/no-target
hard negatives
unknown/reject
```

## Privacidad

- sin transcripción;
- sin identificación de voz;
- ring buffer en memoria;
- descarte por defecto;
- evidencia acústica opcional solo bajo política explícita y retención limitada.

## UX operacional mínima

El consumidor de ECHO necesita saber:

```text
qué se detectó
cuándo
qué source
con qué confianza
qué modelo/config produjo la decisión
si el evento fue confirmado o solo candidato
```

No necesita que ECHO declare causalidad social.