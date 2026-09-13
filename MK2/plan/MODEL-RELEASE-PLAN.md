# Model Release Plan — MK2

1. train candidate reproducibly;
2. evaluate offline holdout;
3. calibration + threshold freeze;
4. long-negative regression;
5. runtime benchmark;
6. shadow/canary against stable model;
7. review false positives/negatives;
8. promote or reject;
9. retain rollback package.

## Shadow mode

El challenger puede recibir las mismas ventanas sin emitir eventos externos. Sus resultados se comparan offline para reducir riesgo de rollout.