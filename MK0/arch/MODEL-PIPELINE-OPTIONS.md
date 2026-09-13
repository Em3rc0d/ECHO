# Model Pipeline Options — MK0

## Baseline A — YAMNet embeddings

- MobileNetV1 depthwise-separable CNN.
- entrada oficial: mono 16 kHz;
- frame ~0.96 s, hop ~0.48 s;
- embedding 1024D;
- 521 clases AudioSet en el modelo publicado por TensorFlow.

Fortaleza: transferencia sencilla y footprint moderado. Riesgo: mismatch entre AudioSet y cámara real.

## Challenger B — PANNs/CNN14

Preentrenado en AudioSet; código oficial publica audio tagging y SED, con modelos CNN y checkpoints. Se debe medir costo de inferencia, embeddings y facilidad de fine-tuning/export.

## Challenger C — compact custom CNN

Log-mel + CNN pequeña entrenada sobre taxonomía ECHO. Sirve como control: puede ser menor y más rápida, pero necesita datos del dominio y puede generalizar peor.

## Exploratorios

AST, HTS-AT, BEATs, PaSST/AudioMAE/CLAP pueden aportar mejor representación, pero no deben entrar al runtime de MK1 sin benchmark de footprint/latencia/licencia/export.

## Regla de selección

No seleccionar por accuracy publicada. Usar el mismo split ECHO y medir calidad, false alarms/hour, latencia, memoria, throughput, facilidad operativa y licencia.