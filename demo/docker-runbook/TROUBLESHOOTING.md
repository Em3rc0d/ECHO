# Docker Demo Troubleshooting

## Preflight says an artifact is missing

Do not install Python/model libraries on the host.

Restore the required `artifacts/` file described in `ARTIFACTS.md`, then rerun:

```bash
docker compose -f compose.mvp.yaml --profile demo run --rm --no-deps demo python scripts/mvp/check_demo_runtime.py
```

## Docker build fails while installing packages

The build needs internet access for:

- base image retrieval;
- apt packages;
- Python packages.

Retry after checking Docker networking/proxy configuration.

Do not work around it by creating a parallel host-Python runtime.

## Demo container exits immediately

Inspect:

```bash
docker compose -f compose.mvp.yaml logs --tail=200 demo
```

Common causes:

- missing selected ECHO head checkpoint;
- missing PANNs checkpoint;
- missing temporal config;
- missing fixture WAV;
- incompatible/stale artifact set.

Run the artifact preflight.

## Broker is unhealthy

Inspect:

```bash
docker compose -f compose.mvp.yaml logs --tail=200 broker
```

MQTT port 1883 is internal to the Compose network by design. Do not expose it to the host merely to make the demo work.

## Consumer is not running

Inspect:

```bash
docker compose -f compose.mvp.yaml logs --tail=200 consumer
```

The demo depends on the broker health check and consumer startup.

## Browser cannot open localhost:8088

Check:

```bash
docker compose -f compose.mvp.yaml --profile demo ps
```

The demo must show a host binding equivalent to:

```text
127.0.0.1:8088->8088/tcp
```

Then retry:

```text
http://localhost:8088
```

## UI appears old after a rebuild

Use a hard refresh:

```text
Ctrl + Shift + R
```

The server itself sends `Cache-Control: no-store`, but a hard refresh is still useful during development.

## Microphone permission is denied

Allow microphone access for `http://localhost:8088` in the browser's site permissions.

If permission was permanently denied, reset the site's microphone permission and reload.

## Microphone recording is rejected as too short

External microphone input must contain at least one complete analysis window.

Current configuration is typically 6 s.

Record longer than the minimum shown in the UI.

This is intentional: short zero-padded clips previously created repeated pseudo-evidence.

## Voice/ambient input shows UNKNOWN

That can be correct for the frozen demo.

`UNKNOWN` means internal target candidate(s) existed but ECHO refused to accept/publish them because external-domain behavior is not field calibrated.

It does not mean the candidate label was correct.

## External target sound still shows UNKNOWN

Also expected.

The professor demo deliberately does not field-calibrate external microphone/WAV input. A target-like candidate remains diagnostic and is not promoted to a field-valid event.

Do not weaken the abstention layer just to make a live target example turn green.

## PANNs labels are materialized on first use

ECHO uses a Docker named volume for PANNs auxiliary data.

The pinned AudioSet label CSV may require network access when the volume is empty.

Removing Compose volumes with `down -v` clears that cache.

## High CPU / slow first analysis

The selected PANNs model runs on CPU unless the container/runtime is explicitly configured otherwise.

The demo prioritizes reproducibility over low-latency hardware tuning.

Do not claim real-time camera performance from professor-demo timing.

## Need a clean restart

```bash
docker compose -f compose.mvp.yaml --profile demo down
docker compose -f compose.mvp.yaml build demo
docker compose -f compose.mvp.yaml --profile demo up -d
```

Use `down -v` only when you intentionally want to remove named volumes too.
