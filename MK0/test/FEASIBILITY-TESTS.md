# Feasibility Tests — MK0

## T-01 Offline inference

Dado WAV mono/estéreo válido, el pipeline candidato genera scores/embeddings reproducibles y timestamps de ventanas.

## T-02 Temporal aggregation

Una secuencia de ventanas positivas debe consolidarse en un solo evento; ventanas aisladas de baja evidencia no deben generar múltiples alarmas.

## T-03 Hard-negative replay

Reproducir confusores cercanos a cada clase y medir false positives por hora equivalente.

## T-04 Noise/SNR

Mezclar positivos con fondos a varios SNR y medir degradación por clase.

## T-05 RTSP smoke

Cuando exista cámara: conectar, extraer audio, detectar stall y reconectar sin bloquear el proceso.

## T-06 Distance field

5/10/15/20/25 m bajo protocolo controlado cuando sea legal/seguro; registrar ruido, orientación y dispositivo.

## T-07 Multi-source synthetic

Multiplexar N streams de replay para descubrir límites de CPU, memoria y backlog antes de disponer de N cámaras físicas.