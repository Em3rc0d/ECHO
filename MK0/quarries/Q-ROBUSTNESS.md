# Quarry — Robustness

## Preguntas

- ¿Cómo cambia recall con SNR, distancia y reverberación?
- ¿Qué confusores dominan cada clase?
- ¿Qué codec/bitrate de cámara degrada transientes como glass break?
- ¿Qué augmentation representa el dominio sin crear artefactos irreales?
- ¿Cómo se comporta el modelo ante viento, música, voz, tráfico y obras?

## Extracciones requeridas

- curvas por SNR;
- matrix evento x hard-negative;
- ablation codec/sample-rate;
- field holdout;
- false alarms/hour en audio largo negativo.

## Criterio de cierre

No cerrar robustez con accuracy de clips balanceados.