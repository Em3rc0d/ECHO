# Privacy & Security — MK1

## Privacy by default

- procesamiento local cuando sea viable;
- audio continuo no persistido por defecto;
- almacenar metadata de eventos y métricas;
- clips de evaluación sólo bajo autorización y con retention explícita;
- no transcribir ni extraer contenido semántico de conversaciones.

## Secret handling

RTSP/ONVIF/MQTT credentials se cargan desde variables/secret store local y jamás se incluyen en manifests, events o logs.

## MQTT

En laboratorio aislado puede usarse configuración simple; cualquier despliegue compartido exige auth/ACL y preferentemente TLS. Publisher identity debe limitar topics permitidos.

## FFmpeg adapter

No concatenar input no confiable en shell commands. Usar argumentos estructurados y allowlists de opciones.

## Supply chain

Checkpoints y artefactos externos se fijan por versión + checksum; licencias/notices se registran antes de distribución.