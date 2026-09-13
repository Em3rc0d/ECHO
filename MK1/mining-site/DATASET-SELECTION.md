# Dataset Selection Evidence — MK1

Este archivo se completa al cerrar la selección exacta.

## Candidate roles

- **FSD50K:** diversidad multi-label y mapeo AudioSet; controlar licencia por clip.
- **ESC-50:** sanity benchmark para siren/car horn; CC BY-NC limita usos fuera del ámbito permitido.
- **UrbanSound8K/SONYC:** dominio urbano potencial; verificar versión/licencia exacta.
- **DCASE/DESED:** referencia metodológica para SED/strong labels; dominio doméstico no representa cámara urbana.
- **ECHO field data:** domain holdout decisivo.

## No permitido

No fusionar datasets por nombre de label sin revisar definición acústica y ontología. `crash`, `impact`, `alarm` pueden tener semánticas incompatibles entre fuentes.