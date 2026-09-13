# Privacy & Compliance Gate

## Principio ECHO

ECHO analiza eventos acústicos. No necesita reconocimiento de voz, transcripción continua ni identificación de hablantes para cumplir su promesa.

## Política certificada de diseño

- `ASR_CONTINUOUS = OFF`
- `SPEAKER_IDENTIFICATION = OFF`
- raw audio retention por defecto = `OFF`
- usar buffers efímeros mínimos para inferencia;
- persistir por defecto metadata/eventos, no conversaciones;
- toda captura de campo debe tener propósito, autorización y política de retención documentados;
- acceso a streams/credenciales bajo mínimo privilegio;
- secretos fuera de Git;
- exportación de clips de evaluación solo si está autorizada y queda registrada en el manifest.

## Contexto normativo peruano

La ANPD mantiene la Ley 29733 y el Reglamento aprobado por DS 016-2024-JUS. También existe la Directiva para tratamiento de datos personales mediante sistemas de videovigilancia aprobada en 2020.

Fuentes:

- https://www.gob.pe/institucion/anpd/normas-legales
- https://www.gob.pe/institucion/anpd/normas-legales/6554453-16-2024-jus
- https://www.gob.pe/institucion/anpd/informes-publicaciones/1938476-directiva-para-el-tratamiento-de-datos-personales-mediante-sistemas-de-videovigilancia

## Gate

**Estado:** `EXTERNAL_GATE_OPEN` para despliegue de campo real.

Antes de una instalación real deben quedar documentados responsable/titular aplicable, propósito, base/autorización correspondiente, información a usuarios cuando aplique, acceso, retención, seguridad y cualquier registro/evaluación exigible.

Este documento es control de ingeniería y trazabilidad, no una opinión jurídica.