# Event Delivery — MK2

## Semántica

El core genera un `CONFIRMED_EVENT` una vez lógicamente. El transporte puede redeliver.

## MQTT path

QoS 1 sigue siendo candidato: at-least-once requiere idempotencia. Persistencia de sesión/broker y client behavior deben probarse, no asumirse.

## Durable path

Si requisitos exigen replay después de outage prolongado, introducir event outbox/store o stream durable (por ejemplo JetStream/RabbitMQ/Kafka según carga) detrás de adapter.

## Outbox candidate

`event engine commit -> local durable outbox -> publisher -> ack -> mark delivered` evita perder eventos entre persistencia y publish, pero añade disco/operación.

## Decision gate

Elegir simple MQTT vs durable outbox a partir del SLO de pérdida/replay, no por moda tecnológica.