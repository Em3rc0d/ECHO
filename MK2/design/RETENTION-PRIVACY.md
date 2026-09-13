# Retention & Privacy — MK2

## Default

ECHO procesa stream y conserva metadata mínima necesaria. Audio continuo no es un artefacto operacional por defecto.

## Event clips opcionales

Si un deployment autorizado requiere clips para auditoría/ML:

- policy explícita por site;
- pre/post buffer acotado;
- cifrado/ACL según entorno;
- TTL definido;
- audit trail de acceso;
- separación entre dataset de investigación y evidencia operacional.

## Sensitive speech

ECHO no necesita ASR/transcripción para cumplir su promesa. No añadirla por conveniencia.

## Data deletion

La arquitectura debe permitir borrar clips/metadata según policy sin invalidar manifests históricos; los manifests conservan hashes/provenance permitidos, no el contenido sensible.