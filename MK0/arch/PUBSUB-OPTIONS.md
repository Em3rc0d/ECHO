# Pub/Sub Options — MK0

## MQTT

Candidato principal para MK1. MQTT 5 es un protocolo publish/subscribe ligero. QoS 1 ofrece entrega **at least once**, por lo que ECHO debe usar `event_id` e idempotencia downstream.

## Mosquitto

Broker liviano, adecuado para PoC local. Debe configurarse con autenticación/TLS cuando salga de un entorno aislado.

## NATS JetStream

Candidato MK2 si se requiere persistencia/replay/consumer state más fuerte. Añade semántica de stream durable y mayor complejidad.

## RabbitMQ

Útil si aparecen routing/queues/ack patterns más ricos. No necesario como default de PoC.

## Kafka

Alta capacidad y replay, pero overhead operativo injustificado para MK1.

## Redis Pub/Sub

No se recomienda como bus crítico si se requiere recuperación de mensajes cuando un subscriber está desconectado.

## Principio

El modelo no publica alarmas directamente. `Inference -> Event Engine -> confirmed event -> publisher` mantiene ML desacoplado de transporte.