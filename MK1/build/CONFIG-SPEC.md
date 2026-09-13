# Configuration Specification — MK1

## Capas

- `config/default.yaml`: valores no secretos;
- `config/taxonomy.yaml`: clases/mappings versionados;
- `config/event-engine.yaml`: thresholds/temporal policies;
- environment/secret provider: URIs, users/passwords;
- CLI overrides sólo para experimentos trazables.

## Validación

Config inválida falla al inicio con mensaje claro. No aplicar defaults silenciosos a campos de seguridad o source URI.

## Snapshot

Cada experimento guarda una copia sanitizada de config efectiva para reproducibilidad.