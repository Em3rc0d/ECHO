# Privacy & Compliance Gate

**Status:** `DESIGN_CERTIFIED / FIELD_GATE_OPEN`

## 1. Principio de minimización

ECHO necesita reconocer fenómenos acústicos, no comprender conversaciones ni identificar personas. Por diseño:

```text
ASR_CONTINUOUS = OFF
SPEAKER_IDENTIFICATION = OFF
VOICE_PROFILING = OFF
RAW_AUDIO_RETENTION_DEFAULT = OFF
```

El camino preferido es audio efímero en memoria -> features/inference -> evento estructurado -> descarte.

## 2. Datos que sí necesita el sistema

Para operar y auditar se conservan, según política:

```text
source_id
site_id
event_type
confidence/calibrated score
timestamps
event_id
model/config/schema versions
source health/runtime telemetry
```

Clips de evidencia solo pueden existir bajo protocolo explícito de evaluación o investigación y con retention/ACL definidos.

## 3. Contexto normativo

En Perú, el proyecto debe considerar la Ley de Protección de Datos Personales N.° 29733, su reglamentación vigente y las reglas/directivas aplicables al tratamiento mediante sistemas de videovigilancia cuando el deployment entre en ese supuesto. Las fuentes normativas se registran en MK0 mining-site.

Este documento es un control de ingeniería, no asesoría jurídica. Una instalación real puede requerir revisión institucional específica.

## 4. Threat/privacy model

Riesgos principales:

- capturar conversaciones incidentalmente;
- retener audio más tiempo del necesario;
- usar clips de prueba fuera de su propósito;
- logs que contengan RTSP URLs con credenciales;
- acceso excesivo al stream;
- reutilizar field data para entrenamiento sin autorización;
- inferir identidad, contenido semántico o conducta más allá de la promesa.

## 5. Controles

- buffers pequeños y bounded;
- retention off por defecto;
- secrets externos a Git;
- red/ACL de mínimo privilegio;
- metadata antes que media;
- clipping/redaction de URIs en logs;
- dataset manifest con `permitted_use`;
- separación de field holdout y training;
- exportación manual/automática de clips deshabilitada salvo política;
- acceso auditado a cualquier evidence store.

## 6. Field gate

Antes de captar audio real deben quedar registrados: propósito, dispositivo/site, responsables/autorización, quién accede, duración de captura, retention, almacenamiento, borrado y si los clips pueden entrar al corpus.

## 7. Testing

MK1/MK2 deben verificar que desactivar retention realmente evita archivos residuales; que logs no exponen passwords; que crashes/temp files no dejan audio; y que consumidores Pub/Sub reciben metadata suficiente sin requerir audio bruto.

## 8. Invalidation

Reabrir si ECHO incorpora ASR, speaker features, evidence clip retention permanente, nube externa, nueva jurisdicción, biometría o un consumidor que requiera media cruda.