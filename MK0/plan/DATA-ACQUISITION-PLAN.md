# Data Acquisition Plan — MK0

## Capas de datos

1. **Public benchmark data:** sirve para smoke tests y representación general.
2. **Curated ECHO data:** subconjunto legalmente utilizable, remapeado a taxonomía ECHO.
3. **Hard negatives:** portazos, metal, obras, música, tráfico, voces, viento, motores y sonidos confusores específicos.
4. **Domain data:** capturado/reproducido mediante la cámara/micrófono objetivo bajo autorización.

## Manifiesto mínimo por asset

`asset_id`, `origin`, `source_url`, `license`, `attribution`, `original_label`, `echo_label`, `duration`, `sample_rate`, `group_id`, `split`, `checksum`, `notes`.

## Leakage

No dividir fragmentos del mismo archivo, uploader o sesión entre train/test cuando puedan compartir firma acústica. FSD50K ya evita mismo uploader entre dev/eval; cualquier remuestreo propio debe conservar grupos.

## AudioSet

Las anotaciones remiten a segmentos de YouTube; disponibilidad puede cambiar. No asumir que es un paquete de WAV estable.

## Field set

Debe reservarse un holdout real de cámara que nunca se use para tuning final.