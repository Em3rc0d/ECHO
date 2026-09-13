# Rollback Plan — MK1

Antes de reemplazar modelo, taxonomy o Event Engine:

1. conservar artefacto/checksum previo;
2. comparar regression suite;
3. versionar configuración;
4. no mezclar thresholds de un modelo con otro sin recalibración;
5. permitir reactivar la versión previa sin migrar raw audio.

## Compatibilidad

Cambios incompatibles de schema incrementan versión mayor. Consumers de PoC deben rechazar versiones desconocidas de forma explícita en vez de interpretar campos silenciosamente.