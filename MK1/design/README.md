# MK1 / Design

Artefactos de diseño:

- `REQUIREMENTS.md`
- `TAXONOMY.md`
- `CONTRACTS.md`

## Diseño del Event Engine

Por `{source_id,event_type}`:

```text
IDLE
  ↓ score >= enter_threshold
CANDIDATE
  ↓ M of N positive windows
CONFIRMED/ACTIVE
  ↓ maintain while evidence persists
CLOSED
  ↓ cooldown/dedup policy
IDLE
```

`enter_threshold > exit_threshold` es candidato para hysteresis.

## Raw inference != event

Ventanas consecutivas del mismo sonido no deben generar N alertas. El Event Engine agrega duración, peak, mean confidence y estado temporal.

## Configuración versionada

Se diseñan como artifacts separados:

```text
labels.yaml
thresholds.yaml
event-engine.yaml
sources.yaml
model-registry.yaml
```

No se implementan hasta que `build` esté READY.