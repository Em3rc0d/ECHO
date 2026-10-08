# ECHO Demo — Docker Runbook

**Status:** `ACTIVE / DEMO_SCOPE_FROZEN`  
**Profile:** `ECHO-MVP-001`  
**Runtime rule:** Docker-only

This folder is the reproducible operator guide for launching the current ECHO professor demo on another machine.

The host needs only:

- Git;
- Docker Engine / Docker Desktop with Docker Compose v2;
- a modern browser.

Do **not** install Python, FFmpeg, Mosquitto, TensorFlow, PyTorch or PANNs on the host for this demo. They belong inside the ECHO container.

## 1. What this demo contains

The current demo exercises:

```text
controlled validation WAV
or blind user WAV
or ephemeral browser microphone capture
        ↓
FFmpeg decode
        ↓
selected PANNS_CNN14_HEAD
        ↓
Temporal Event Engine
        ↓
decision layer
        ↓
echo.event.v1 / MQTT where publication is authorized
```

Current learned target classes:

- `GLASS_SHATTER`
- `SIREN`
- `VEHICLE_HORN`

External microphone/WAV input is not field calibrated. It can return:

- `NO_TARGET` — no current target was temporally confirmed;
- `UNKNOWN` — one or more internal target candidates existed, but ECHO abstains.

Under `ECHO-DEMO-ABSTENTION-v1`, external target candidates are shown for diagnosis but are **not published to MQTT as accepted target events**.

## 2. Important portability boundary

A Git clone alone is not currently enough to execute the ML demo.

The repository deliberately ignores `artifacts/`, audio files and model checkpoints. A runnable installation therefore needs the runtime artifact set described in `ARTIFACTS.md`.

This is intentional:

- trained/generated artifacts are not source code;
- some upstream model/checkpoint redistribution rights require separate governance;
- large media/model binaries do not belong in Git history.

For a machine receiving an already prepared ECHO demo bundle, copy the supplied `artifacts/` directory into the repository root before starting.

For a public reproduction without an artifact bundle, regenerate/provision those artifacts through the governed MVP pipeline before using this runbook.

## 3. Clone

```bash
git clone https://github.com/Em3rc0d/ECHO.git
cd ECHO
git checkout main
git pull --ff-only origin main
```

## 4. Place runtime artifacts

Expected layout:

```text
ECHO/
├── artifacts/
│   ├── models/
│   │   └── panns/
│   │       └── Cnn14_mAP=0.431.pth
│   ├── mvp-benchmark/
│   │   ├── selection.json
│   │   └── panns/
│   │       └── <selected ECHO head checkpoint>.pth
│   └── mvp-temporal/
│       ├── fixtures.json
│       ├── temporal-event-config.json
│       └── streams/
│           └── *.wav
├── compose.mvp.yaml
└── ...
```

The exact selected ECHO head filename is resolved from `selection.json`; do not rename it arbitrarily.

See `ARTIFACTS.md` for details.

## 5. Build the image

From the repository root:

```bash
docker compose -f compose.mvp.yaml build demo
```

The image contains Python 3.12, FFmpeg and the pinned ECHO MVP dependencies.

The first build requires internet access for Docker base images and Python packages.

## 6. Run the artifact preflight

Before starting services:

```bash
docker compose -f compose.mvp.yaml --profile demo run --rm --no-deps demo python scripts/mvp/check_demo_runtime.py
```

Expected final lines:

```text
[READY] Runtime artifact set is sufficient to start the Docker demo.
[BOUNDARY] This preflight checks presence/shape only. It does not certify field performance or production readiness.
```

Do not continue if the preflight reports `[FAIL]`.

## 7. Start the demo

```bash
docker compose -f compose.mvp.yaml --profile demo up -d
```

This starts:

- Mosquitto broker on the internal Compose network;
- ECHO MQTT consumer;
- ECHO demo server.

MQTT port 1883 is **not exposed to the host**.

The demo UI is bound only to:

```text
127.0.0.1:8088
```

## 8. Check service state

```bash
docker compose -f compose.mvp.yaml --profile demo ps
```

Then inspect logs:

```bash
docker compose -f compose.mvp.yaml logs --tail=100 broker consumer demo
```

For live logs:

```bash
docker compose -f compose.mvp.yaml logs -f demo
```

## 9. Open the UI

Open:

```text
http://localhost:8088
```

If a stale browser copy is visible, use a hard refresh.

Chrome/Edge:

```text
Ctrl + Shift + R
```

The browser will request microphone permission only when the ambient-capture feature is used.

## 10. Minimum functional verification

Follow `VALIDATION.md`.

At minimum confirm:

1. the four controlled scenarios load;
2. controlled target scenarios execute through ECHO;
3. the controlled negative scenario runs;
4. a blind WAV can be selected;
5. a microphone recording of at least the configured analysis-window duration can be analyzed;
6. external audio shows `NO_TARGET` or `UNKNOWN`;
7. `UNKNOWN` candidates are marked `NO PUBLICADO`;
8. external abstention does not publish a target event to MQTT;
9. score diagnostics are visible.

## 11. Stop

```bash
docker compose -f compose.mvp.yaml --profile demo down
```

This keeps the named PANNs auxiliary-data volume.

To also remove Compose volumes:

```bash
docker compose -f compose.mvp.yaml --profile demo down -v
```

Removing the volume can require the pinned PANNs label metadata to be materialized again on a later run.

## 12. Update an existing installation

```bash
git pull --ff-only origin main
docker compose -f compose.mvp.yaml build demo
docker compose -f compose.mvp.yaml --profile demo run --rm --no-deps demo python scripts/mvp/check_demo_runtime.py
docker compose -f compose.mvp.yaml --profile demo up -d
```

Hard-refresh the browser after rebuilding.

## 13. What a successful demo does not prove

A successful local launch proves that the packaged demo/runtime path operates on that installation.

It does **not** prove:

- production readiness;
- camera-domain performance;
- zero false positives;
- field calibration;
- a learned OOD detector;
- support for classes beyond the current three;
- a maximum operating distance.

See `../../MK1/test/FALSE-POSITIVE-ANALYSIS-2026-10-08.md` and `../DEMO-SCOPE-FREEZE.md`.

## 14. Support path

If launch fails, use `TROUBLESHOOTING.md` before changing model thresholds or source code.

If a runtime artifact is missing, fix the artifact set rather than installing ML dependencies on the host.
