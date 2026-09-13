# ECHO Data Foundry — Intake spec examples

These examples are operator templates. Replace paths with verified local landing/extraction paths; do not commit raw media.

## FSD50K

```json
{
  "schema_version": "echo.intake-spec.v1",
  "adapter": "fsd50k",
  "parameters": {
    "csv_path": "/data/fsd50k/FSD50K.ground_truth/dev.csv",
    "partition": "dev",
    "vocabulary_csv": "/data/fsd50k/FSD50K.ground_truth/vocabulary.csv",
    "clip_info_json": "/data/fsd50k/FSD50K.metadata/dev_clips_info_FSD50K.json",
    "audio_root": "/data/fsd50k/FSD50K.dev_audio"
  }
}
```

## SONYC-UST

```json
{
  "schema_version": "echo.intake-spec.v1",
  "adapter": "sonyc",
  "parameters": {
    "csv_path": "/data/sonyc/annotations.csv",
    "audio_root": "/data/sonyc/audio"
  }
}
```

## SINGA:PURA

```json
{
  "schema_version": "echo.intake-spec.v1",
  "adapter": "singapura",
  "parameters": {
    "metadata_csv": "/data/singapura/labelled_metadata_public.csv",
    "labels_dir": "/data/singapura/labels",
    "audio_root": "/data/singapura/audio"
  }
}
```

ESC-50 and UrbanSound8K use the same pattern with adapters `esc50` and `urbansound8k` plus `csv_path` and `audio_root`.
