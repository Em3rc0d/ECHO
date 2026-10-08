# Runtime Artifacts Required by the Docker Demo

The demo source code is versioned in Git. The current ML/runtime binaries and generated fixtures are not.

## Required files

### 1. PANNs pretrained checkpoint

```text
artifacts/models/panns/Cnn14_mAP=0.431.pth
```

This is the pretrained PANNs Cnn14 backbone checkpoint used by the selected ECHO model path.

It is not downloaded implicitly by the professor-demo server.

Checkpoint provenance/licensing remains governed by `THIRD_PARTY.md`.

### 2. ECHO benchmark selection

```text
artifacts/mvp-benchmark/selection.json
```

The file identifies the selected benchmark arm and the selected ECHO head checkpoint.

The active demo expects:

```text
PANNS_CNN14_HEAD
```

### 3. Selected ECHO head checkpoint

The exact filename comes from:

```text
selection.json -> winner.checkpoint
```

The demo resolver supports the selected PANNs head under:

```text
artifacts/mvp-benchmark/panns/<checkpoint filename>
```

Do not invent a replacement checkpoint or rename another model to satisfy the path.

### 4. Temporal Event Engine config

```text
artifacts/mvp-temporal/temporal-event-config.json
```

Expected boundary:

```text
CONTROLLED_VALIDATION_CALIBRATED_NOT_FIELD_CALIBRATED
```

Expected current labels:

```text
GLASS_SHATTER
SIREN
VEHICLE_HORN
```

### 5. Controlled demo fixture catalog

```text
artifacts/mvp-temporal/fixtures.json
```

It must resolve four demo scenario families:

- glass-shatter burst;
- siren burst;
- vehicle-horn burst;
- negative/background stream.

### 6. Controlled fixture WAV files

Normally:

```text
artifacts/mvp-temporal/streams/*.wav
```

The paths referenced by `fixtures.json` must resolve on the local installation.

## Preflight

Run:

```bash
docker compose -f compose.mvp.yaml run --rm --no-deps demo   python scripts/mvp/check_demo_runtime.py
```

The checker validates presence and structural expectations for this demo.

It does not validate model accuracy or field behavior.

## Why these files are not committed

The repository `.gitignore` intentionally excludes:

- `artifacts/`;
- audio media;
- `*.pth` / `*.pt` model files;
- other generated ML artifacts.

That protects Git history from large/generated binaries and avoids silently redistributing third-party checkpoints or media without explicit rights review.

## Distribution rule

Do not publish an artifact bundle merely because it works locally.

Before redistribution, verify:

- PANNs checkpoint provenance and permitted redistribution;
- source media rights for controlled fixture WAVs;
- ECHO-generated checkpoint release policy;
- hashes/manifests for the exact bundle.

A private/internal authorized bundle can be copied into `artifacts/` and checked with the preflight command.

A public reproducibility package requires its own governed release artifact, not an ad hoc ZIP.
