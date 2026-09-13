# Dataset Landscape

| Dataset | Naturaleza | Clases/valor para ECHO | Licencia / condición | Uso propuesto |
|---|---|---|---|---|
| AudioSet | >2M segmentos etiquetados de YouTube; ontología amplia | base de YAMNet/PANNs; mapping semántico | metadata/YouTube availability; no asumir redistribución de audio | pretraining/taxonomía/reference |
| FSD50K | 51,197 clips, 200 clases, >100 h | eventos ambientales variados | licencia por clip; incluye CC0/CC-BY/CC-BY-NC/Sampling+ | pool principal filtrado por licencia |
| ESC-50 | 2,000 clips, 50 clases, 5 folds | siren, car horn, glass breaking, engine, etc. | CC BY-NC para dataset completo | benchmark académico/reproducibilidad |
| UrbanSound8K | 8,732 clips, 10 clases | horn, siren, drilling, engine, jackhammer | CC BY-NC 3.0 | benchmark/domain urban |
| SONYC-UST / V2 | red real de sensores, multilabel | ruido urbano/polyphony/contexto | verificar release exacto | arquitectura de sensor + robustness |
| MIMII | maquinaria normal/anómala + factory noise | domain shift/industrial noise | CC BY-SA 4.0 en release original | robustness/anomaly research |
| DCASE/DESED tasks | SED con weak/strong labels | temporal localization, overlapping events | depende del task/release | metodología SED/evaluation |
| ECHO Field Dataset | por construir | dominio real de la cámara/ambiente | governance propia | decisivo para MK1/MK2 |

## No confundir “contiene una clase” con “sirve para producción”

Para integrar una muestra se requiere:

```text
origin URL
source dataset
asset/license
sha256
label provenance
session/source grouping
permitted_use
split
```

## Split policy

Nunca mezclar segmentos provenientes del mismo evento físico/grabación/sesión entre train y test.

Agrupar por, cuando exista:

```text
original recording
session
site
device/microphone
physical event
```

Además mantener un **field holdout** completamente separado.

## Background / negatives

No depender de `OTHER` como bolsa infinita. Construir:

- background/no-target;
- hard negatives;
- unknown/reject state;
- confusores por clase.

Hard negatives candidatos: speech, music, door slam, metal/rock impacts, engines, traffic, wind, rain, radio, normal machinery, construction sounds y otros ruidos frecuentes del ambiente real.

## Metadata de campo

Registrar:

```text
recording_id
site_id
source_id
camera_model
microphone_model
codec
sample_rate_original
distance_m
orientation/weather/noise state
event_type
onset/offset
annotator
label_quality
```

## Fuentes

- AudioSet: https://research.google.com/audioset/
- FSD50K: https://zenodo.org/records/4060432
- ESC-50: https://github.com/karolpiczak/ESC-50
- UrbanSound8K: https://zenodo.org/records/1203745
- SONYC-UST: https://zenodo.org/records/3966543
- MIMII: https://zenodo.org/records/3384388
- DCASE: https://dcase.community/