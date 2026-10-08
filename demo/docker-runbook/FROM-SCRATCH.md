# From-Scratch MVP Artifact Regeneration (Advanced)

Use this only when you do **not** have an authorized prepared `artifacts/` bundle.

The normal professor-demo path is faster: obtain the governed runtime artifacts, run the preflight, and start the demo.

This advanced path executes the MVP materialization/benchmark pipeline inside Docker. It can be slow, download substantial external data/models, and depends on upstream source availability and rights.

## 1. Build the ECHO image

```bash
docker compose -f compose.mvp.yaml build demo
```

## 2. Execute the resumable MVP pipeline in Docker

```bash
docker compose -f compose.mvp.yaml --profile demo run --rm --no-deps demo python scripts/mvp/execute_mvp.py
```

The command performs the repository-defined preflight, synthetic core smoke, frozen-snapshot check, media materialization, pinned PANNs checkpoint fetch, A/B/C benchmark, selection artifact generation and selected-model smoke unless explicitly skipped.

Default device is CPU.

The environment preflight currently enforces at least 2 GiB free as a fail-fast floor, but practical reproduction should keep substantially more free space for Docker layers, media, feature caches and checkpoints.

## 3. Run controlled temporal calibration

After `selection.json` and the media cache exist:

```bash
docker compose -f compose.mvp.yaml --profile calibration run --rm temporal-calibration
```

Expected outputs include:

```text
artifacts/mvp-temporal/fixtures.json
artifacts/mvp-temporal/streams/*.wav
artifacts/mvp-temporal/scores/*.jsonl
artifacts/mvp-temporal/score-summary.json
artifacts/mvp-temporal/calibration-report.json
artifacts/mvp-temporal/temporal-event-config.json
```

## 4. Run the demo artifact preflight

```bash
docker compose -f compose.mvp.yaml --profile demo run --rm --no-deps demo python scripts/mvp/check_demo_runtime.py
```

Only continue after `[READY]`.

## 5. Start the demo

```bash
docker compose -f compose.mvp.yaml --profile demo up -d
```

Open:

```text
http://localhost:8088
```

## Reproducibility boundary

This repository contains the orchestration/code required by the current MVP path, but a future clean-room reproduction can still fail for reasons outside ECHO source control, including:

- upstream media becoming unavailable;
- network/proxy restrictions;
- upstream model hosting changes;
- disk/memory limits;
- third-party package ecosystem changes.

Do not replace missing governed media with arbitrary clips and then call the result the same frozen benchmark.

Do not redistribute downloaded media or checkpoints without verifying the rights recorded in `THIRD_PARTY.md` and the applicable source manifests.

For presentation/evaluation, prefer a separately governed artifact bundle once a redistribution-safe demo release is prepared.
