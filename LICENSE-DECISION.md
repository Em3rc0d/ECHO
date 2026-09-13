# License Decision

**Status:** `OPEN_OWNER_DECISION`  
**Scope:** licencia del código propio de ECHO; no cubre assets de terceros.

## 1. Problema

ECHO usa o evalúa software, modelos preentrenados, checkpoints, datasets, codecs, brokers y herramientas con licencias diferentes. Elegir una licencia para el código propio no convierte automáticamente todo el sistema en redistribuible bajo esa misma licencia.

## 2. Capas que deben separarse

```text
ECHO-owned source code
third-party source libraries
runtime binaries
model architecture code
pretrained checkpoint
training/evaluation dataset
individual audio asset
container/base image
standards/specifications
```

Cada capa necesita provenance y términos propios.

## 3. Alternativas para el código ECHO

### Apache-2.0

Ventajas: permisiva, incluye grant explícito de patentes y es familiar en ecosistemas de ML/infra. Facilita uso académico y potencial reutilización comercial. Requiere conservar licencia/notices y gestionar correctamente terceros.

### MIT

Ventajas: simple y permisiva. Menor carga documental. No contiene la misma formulación explícita de patent grant de Apache-2.0.

### GPL-family

Ventaja: obliga a mantener determinadas libertades en derivados/distribución. Desventaja para ECHO: puede complicar integración y distribución futura cuando el objetivo aún no ha decidido una política copyleft.

## 4. Posición actual

`DECISION_CANDIDATE`: Apache-2.0 es la candidata preferida para **código original ECHO**, pero el repositorio no crea un `LICENSE` definitivo sin decisión explícita del propietario.

La decisión no bloquea el desarrollo interno de MK1; sí bloquea una release/distribución formal que se presente como licenciada.

## 5. Terceros relevantes

- TensorFlow / YAMNet: verificar versión y notices exactos.
- PANNs y challengers: separar licencia del repositorio de la del checkpoint.
- FFmpeg: su resultado de licenciamiento depende de build/options; no asumir que cualquier binario tiene idénticas obligaciones.
- GStreamer: revisar plugins usados y dependencias concretas.
- Mosquitto: registrar versión y licencia del broker.
- Datasets: una licencia a nivel dataset no sustituye licencias por asset cuando el release es mixto.

## 6. Release gate

Antes de un release distribuible deben existir:

```text
LICENSE
THIRD_PARTY.md actualizado
SBOM/dependency inventory
checkpoint provenance
asset-license manifest
notices/attributions
record del build de FFmpeg/GStreamer si se empaqueta
```

## 7. Riesgos

- entrenar con assets NC y luego presentar el modelo como irrestrictamente comercial;
- redistribuir media de YouTube por confundir metadata de AudioSet con derechos del audio;
- asumir que la licencia del repo del modelo aplica automáticamente al checkpoint;
- empaquetar un build de FFmpeg con componentes de obligaciones distintas sin registrarlo;
- perder attribution/provenance al copiar datasets.

## 8. Validación

La validación final se realiza sobre el BOM real de release, no sobre una lista conceptual. Todo asset se audita por versión/hash y términos vigentes del artefacto usado.

## 9. Invalidation

Reabrir este documento si cambia el objetivo de distribución, se incorpora un componente copyleft/NC, se reemplaza un checkpoint o se decide distribuir datasets/audio junto al producto.