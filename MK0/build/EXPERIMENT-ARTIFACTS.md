# Experiment Artifacts — MK0

Cuando BUILD sea habilitado, cada experimento debe producir:

```text
experiments/<experiment_id>/
  manifest.yaml
  config.yaml
  environment.txt
  metrics.json
  per_class.csv
  latency.json
  artifacts.sha256
  notes.md
```

`manifest.yaml` enlaza dataset version, git SHA, model/checkpoint, preprocessing, hardware y seed. Ningún resultado manual sin provenance puede cerrar un gate.

Los datasets raw, credenciales y audio sensible no se versionan en Git. Se versionan manifests/checksums y rutas externas autorizadas.