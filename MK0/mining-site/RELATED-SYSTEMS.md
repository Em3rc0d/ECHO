# Related Systems — Evidence Notes

## Frigate

Sistema NVR open source orientado a cámaras. Relevancia ECHO: ingestión por cámara, FFmpeg, audio detection y MQTT. Lección: separar estado/configuración por cámara y eventos del transporte. Diferencia: ECHO tiene como promesa central la detección/clasificación acústica, no NVR/video.

## PANNs inference

Interfaz pública para audio tagging/SED basada en PANNs. Lección: un backbone preentrenado puede reutilizarse para tagging y ventanas de SED, pero la lógica temporal de producto sigue siendo responsabilidad de ECHO.

## TensorFlow YAMNet examples

Demuestran extracción de embeddings y transfer learning con pocas capas adicionales. Lección: baseline de bajo riesgo para MK1; no demuestra robustez de cámara.

## DCASE baselines

DCASE/DESED formaliza weak vs strong labels, eventos temporales y evaluación de SED. Lección: distinguir clip classification de temporal detection y no entrenar/testear con leakage.

## Lo que sigue siendo ingeniería ECHO

- taxonomía y label mapping propios;
- domain adaptation a vigilancia;
- Event Engine temporal;
- source abstraction multi-source;
- contratos versionados;
- false-alarm control y calibration;
- observabilidad, resiliencia, privacy y certification DAG.