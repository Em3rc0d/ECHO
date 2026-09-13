# Dataset Landscape — audited

**Audit:** 2026-09-13

| Dataset | Facts auditados | Licencia/condición | Rol ECHO | Estado |
|---|---|---|---|---|
| AudioSet | 2,084,320 segmentos humanos de 10 s; 527 labels anotados; ontología amplia | metadata/dataset release CC BY 4.0; ontology CC BY-SA 4.0; no asumir derechos sobre media YouTube subyacente | ontology, mapping, pretrained backbones, metadata research | CERTIFIED_REFERENCE |
| FSD50K | 51,197 clips; 108.3 h; 200 clases; multilabel; weak clip labels; eval exhaustive | licencia **por clip**: CC0/CC-BY/CC-BY-NC/Sampling+; curation dataset CC-BY | pool de assets con filtro explícito por licencia + negatives | CERTIFIED_WITH_ASSET_FILTER |
| SONYC-UST v2 | sensor network urbano real; 23 fine/8 coarse; multilabel; sensor-disjoint train/val; test desplazado temporalmente | revisar release exacto en manifest; Zenodo es fuente autoritativa | domain robustness, urban multilabel, horn/siren/alarm/reverse-beeper context | CERTIFIED_REFERENCE |
| ESC-50 | 2,000 clips de 5 s, 50 clases, folds oficiales | dataset completo CC BY-NC; no usar como supuesto asset comercial | benchmark académico, confusores, reproducibilidad | CERTIFIED_RESEARCH_ONLY |
| UrbanSound8K | corpus urbano con folds; useful horn/siren/context | verificar release/licencia exacta en manifest antes de asset use | benchmark urbano secundario | CANDIDATE_ASSET_SOURCE |
| DCASE / DESED releases | SED weak/strong/synthetic methodology; polyphonic evaluation | depende del task/release exacto | SED methodology, temporal metrics, PSDS/evaluation | CERTIFIED_METHODOLOGY |
| ECHO Field Dataset | aún inexistente | gobernanza/consent/retention propia | dominio decisivo para camera/device/SNR/distance | EXTERNAL_BUILD_ARTIFACT |

## Asset admission rule

Ningún audio entra al corpus ECHO entrenable/evaluable sin:

```text
asset_id
origin_url
source_dataset + release
author/uploader when required
asset_license
permitted_use
sha256
original_recording/group_id
labels + label_provenance
split
imported_at
```

Si la licencia del clip es NC/restringida, el manifest debe impedir que el asset se mezcle silenciosamente con un corpus destinado a usos incompatibles.

## Split / leakage policy

Nunca mezclar el mismo evento físico, recording, session o source-equivalent entre train y test.

Prioridad de grouping:

```text
physical_event > original_recording > session > device/source > site
```

Conservar splits oficiales cuando su diseño evita leakage (p. ej. folds del corpus o sensor-disjoint splits). Además, ECHO mantiene un `field_holdout` independiente.

## Target evidence

MK1 usa cinco targets:

- `GLASS_SHATTER`
- `SIREN`
- `FIRE_ALARM`
- `VEHICLE_HORN`
- `TIRE_SQUEAL`

AudioSet respalda la existencia/semántica de estos nodos o de sus padres/children. La disponibilidad en un dataset no basta: cada asset seleccionado debe validar semántica y licencia.

## Negatives

No existe una bolsa `OTHER` infinita. Se construyen:

- `BACKGROUND_NO_TARGET`;
- hard negatives específicos por target;
- OOD/reject scenarios;
- confusores reales del ambiente.

## Fuentes primarias

- AudioSet: https://research.google.com/audioset/
- AudioSet license/download: https://research.google.com/audioset/download.html
- FSD50K: https://zenodo.org/records/4060432
- SONYC-UST v2: https://zenodo.org/records/3966543
- ESC-50: https://github.com/karolpiczak/ESC-50
- DCASE: https://dcase.community/