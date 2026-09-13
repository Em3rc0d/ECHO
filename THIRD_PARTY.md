# Third-Party Registry

**Status:** `GOVERNANCE_CERTIFIED / RELEASE_BOM_PENDING`

## 1. Objetivo

Registrar dependencias, modelos, datasets y herramientas externas de forma separada del código propio. Este archivo describe la política y el inventario conocido; el BOM final debe generarse sobre versiones exactas de una build real.

## 2. Software y protocolos

| Componente | Rol | Consideración | Acción obligatoria antes de release |
|---|---|---|---|
| TensorFlow / YAMNet | baseline A | versionado de runtime y modelo | pin de versión + hash + notices |
| PANNs/Cnn14 | challenger B | repo y checkpoint deben auditarse por separado | provenance del checkpoint |
| custom ECHO CNN | control C | código propio + librerías numéricas | licencia ECHO + dependency BOM |
| FFmpeg | ingest/decode baseline | obligaciones dependen del build/config | registrar binario/build exacto |
| GStreamer | fallback/challenger streaming | plugins pueden introducir licencias distintas | listar plugins exactos |
| go2rtc | relay opcional | no es dependencia core | pin solo si se incorpora |
| Eclipse Mosquitto | broker MQTT | servicio/binary independiente | version + config + notices |
| MQTT 5.0 | protocolo | estándar, no dependencia de código | documentar versión semántica |
| ONVIF Profile T | discovery/profile | estándar/interoperabilidad | usar solo features necesarias |

## 3. Modelos y checkpoints

Un modelo se admite únicamente con:

```yaml
model_id:
upstream_repository:
architecture_version:
checkpoint_uri:
checkpoint_sha256:
code_license:
checkpoint_license:
pretraining_dataset:
runtime_dependencies:
permitted_use:
```

La ausencia de licencia explícita de un checkpoint impide asumir derechos de redistribución.

## 4. Datasets

### AudioSet

Usar como ontología/referencia y provenance de pretraining. No confundir las licencias publicadas para metadata/ontology con derechos de redistribución del media subyacente de YouTube.

### FSD50K

El release contiene licencias por clip. El manifest ECHO debe registrar el asset individual y filtrar por uso permitido.

### ESC-50 / UrbanSound8K

Útiles como benchmarks académicos y contraste de dominio; sus términos impiden tratarlos automáticamente como corpus de producción irrestricto.

### SONYC / DCASE / DESED / MIMII

Auditar por release/task exacto. No existe una política universal para todos los datasets alojados bajo una misma comunidad.

## 5. Asset admission

Ningún audio, checkpoint o binary entra a un artefacto reproducible sin:

```text
origin
version/release
hash
license
permitted_use
attribution requirement
redistribution flag
```

Estado desconocido = `QUARANTINED`.

## 6. Supply-chain risks

- checkpoint sustituido upstream sin versionado;
- dependencia transitiva con licencia incompatible;
- modelo descargado desde mirror no oficial;
- binario FFmpeg diferente al documentado;
- archivo de dataset modificado tras generar splits;
- base image/container con paquetes no inventariados.

## 7. Release outputs

MK2 debe producir SBOM, model manifest, dataset/asset manifest, notices y hashes de artefactos. Estos outputs alimentan el certification DAG y deben poder compararse entre releases.

## 8. Invalidation

Actualizar el registro cuando cambie una dependencia, versión, checkpoint, dataset release, política de distribución o cuando un upstream modifique licencia/términos.