# Chaos / Fault Injection — MK2

Fault injection controlado valida assumptions de arquitectura.

## Experimentos

- latencia artificial en source;
- packet/drop simulation en laboratorio;
- kill/restart de worker;
- broker unavailable;
- CPU throttling;
- disk pressure;
- malformed/non-audio stream;
- time jump/timestamp discontinuity.

Nunca ejecutar fault injection contra infraestructura ajena/no autorizada. El alcance es el entorno de prueba de ECHO.