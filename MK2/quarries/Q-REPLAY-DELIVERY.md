# Quarry — Replay & Delivery

¿Cuánto replay necesita el producto después de outage? ¿event store local basta? ¿MQTT persistent sessions cubren el requisito? ¿se necesita outbox/JetStream/RabbitMQ/Kafka?

La respuesta depende de RPO/RTO y volumen. MK2 no debe adoptar infraestructura durable pesada sin requisito cuantificado.