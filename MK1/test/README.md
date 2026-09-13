# MK1 / Test

## Pirámide

```text
unit
  ↓
contract/schema
  ↓
integration
  ↓
stream replay
  ↓
e2e
  ↓
field
```

## Unit

- window boundaries;
- event state transitions;
- hysteresis;
- dedup/idempotency;
- config validation;
- timestamp behavior.

## Integration

- decoder -> preprocessor;
- model -> event engine;
- event -> MQTT;
- event -> storage/query.

## Replay

Horas de background/no-target + targets insertados con ground truth para medir falsas alarmas y latency.

## E2E

```text
source -> confirmed event -> subscriber receives payload
```

## Failure tests

- source disconnect;
- malformed stream;
- broker unavailable;
- slow inference;
- queue saturation;
- duplicate message;
- invalid config/model hash.

## Field

Ejecutar protocolo de distancia/ambiente una vez cerrados external gates.