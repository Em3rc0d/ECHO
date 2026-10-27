# Docker operation and recovery

Status: PROCEDURE_WRITTEN / NOT_EXECUTED. Run from the repository root.
These commands are for the validating operator; the implementation agent did
not run them. Docker Compose >=2.24.4 is required for the optional VPS override.

## 1. Prepare artifacts and secrets

Reuse the existing MVP artifact preparation process in
`demo/docker-runbook/ARTIFACTS.md` and `FROM-SCRATCH.md`. Required files include:

* `artifacts/mvp-benchmark/selection.json` and selected head artifacts it references;
* `artifacts/models/panns/Cnn14_mAP=0.431.pth`;
* `artifacts/mvp-temporal/temporal-event-config.json`;
* `artifacts/mvp-temporal/fixtures.json` and all referenced fixture WAVs.

Operator does not invent model weights or replace these files. Missing artifacts
are an external start gate. Stop the old lab stack when CPU resources are limited;
these are independent Compose projects and can otherwise run duplicate workers.

POSIX preparation:

```bash
cp operator/.env.example operator/.env
mkdir -p operator/secrets artifacts/live-monitor
chmod 700 operator/secrets
docker build -f operator/docker/Dockerfile -t echo-operator:local .
docker run --rm --user 0 --entrypoint node -v "$PWD/operator/secrets:/out" echo-operator:local /app/tools/init-secrets.mjs
```

PowerShell equivalent for first setup:

```powershell
Copy-Item operator/.env.example operator/.env
New-Item -ItemType Directory -Force operator/secrets, artifacts/live-monitor
docker build -f operator/docker/Dockerfile -t echo-operator:local .
docker run --rm --user 0 --entrypoint node --mount "type=bind,source=$($PWD.Path)/operator/secrets,target=/out" echo-operator:local /app/tools/init-secrets.mjs
```

Secure the host secrets directory with account-only permissions/ACLs. The
individual files are read-only and readable by the non-root container via
Compose secret file mounts. Never commit or publish them. Initialization does
not replace existing passwords or a complete VAPID pair; a partial pair fails
explicitly. VAPID rotation invalidates existing push subscriptions.

Edit `operator/.env`: keep `PUBLIC_ORIGIN=http://localhost:8090` for local use,
set a real `VAPID_SUBJECT=mailto:...` and set `ENABLE_LAB_PUSH=true` only when
testing explicitly labeled delivery. `127.0.0.1` and `localhost` are different
origins: use exactly the configured origin. The default listener is loopback.

## 2. Start

```bash
docker compose --env-file operator/.env -f compose.operator.yaml up -d --build
docker compose --env-file operator/.env -f compose.operator.yaml ps -a
docker compose --env-file operator/.env -f compose.operator.yaml logs --tail=100 gateway echo-rtsp-worker vmt-camera-emulator
```

Open `http://localhost:8090`. Sign in as the configured BOOTSTRAP_USER (`admin`
by default). Read the initial password locally from
`operator/secrets/bootstrap_password` with your editor or `Get-Content`.
Do not include it in screenshots, issue reports or chat. Bootstrap is insert-only:
changing its secret file does not reset an existing user's password.

Migrations run before bootstrap, and bootstrap before gateway. Failure stops the
dependency chain instead of serving a partially migrated API. Long-running
services restart independently. Secrets must exist before Compose can start.

## 3. Demonstrate the real path

For the multichannel RTSP stability investigation, follow
[`RTSP-VALIDATION.md`](RTSP-VALIDATION.md). A worker heartbeat is distinct from
recent inference; inspect per-source diagnostics before attributing a failure
to the acoustic model.

1. Sign in; inspect four camera identities and camera MQTT state separately from
   fresh inference. Do not assume a green camera means the scorer is caught up.
2. Select a source; open its HLS player and enable audio with browser controls.
   In browser Network, inspect master → audio/video playlists → init/segments:
   master cookieCheck 302 is handled inside the gateway, child requests preserve
   MediaMTX `session`, and every browser URL remains under `/api/media/<source>/`.
   No upstream cookie/redirect should appear in the browser response. Do not
   paste session query values into logs, issues or screenshots. Test switching
   cameras, reopening the player, invalid/expired sessions and an unauthorized
   site's media URL; permissions apply to every resource.
3. Change `negative` to `siren`. The command response acknowledges the broker;
   inspect subsequent MQTT camera generation/scenario for observed execution.
4. Wait for a complete 6s window and real scoring. Inspect envelope, scores,
   snapshot age, estimated lag, worker session and temporal lifecycle.
5. Inspect the LAB_DIAGNOSTIC event in history. It must not create an operational
   alert. An empty Alert Center is correct while acceptance profiles are empty.
6. Take a camera offline, then online or restart. Observe state, staleness and
   a new worker session. HLS playback may need reopening after a fatal media error.
7. In Settings, register Web Push. If lab delivery is enabled, send a test. It
   must say PRUEBA DE LABORATORIO, and deliveries show provider acceptance only.

Mobile installation and Web Push need a browser-supported secure origin. Desktop
localhost is a local secure-context exception; a phone visiting the computer's
plain HTTP LAN IP is not the same setup. For a phone demo use a user-approved
HTTPS host with a trusted certificate and matching PUBLIC_ORIGIN. This runbook
does not provision or authorize a tunnel, paid service or public deployment.

## 4. Written tests — human execution only

Use a disposable/local stack with a backup. The integration test inserts unique
TEST sources/users and deletes them afterwards. It does not certify the model.

```bash
docker compose --env-file operator/.env -f compose.operator.yaml exec -e ECHO_OPERATOR_TEST_ALLOWED=true gateway npm test
```

Without the explicit environment variable, the DB/API integration case is
SKIPPED. Record skips as skips, never as completed acceptance. Unit cases check
contract rejection and routing defaults. Manual MQTT, media, push, mobile,
accessibility, resilience and capacity cases remain in the acceptance matrix.

PR #57 HLS review correction adds seven scripted transport regression test
cases in `operator/gateway/test/hls.test.ts`: no live MediaMTX is required for
those cases, but they must still be executed later by the validating operator.
They cover the cookie-check/query fallback chain, audio/video playlist session
propagation, direct responses, forbidden redirects, loops, paths/query validation
and cancellation. The DB/API test also checks that media session parameters do
not bypass source/site authorization or a disabled source.

## 5. Backup and restore

Secrets, model artifacts and application DB have different recovery needs. Back
up secrets separately with restricted/encrypted storage. Preserve exact VAPID
keys when retaining subscriptions. Record the Git SHA, image digest, schema
migration hashes and artifact/checkpoint hashes with every backup.

POSIX (custom pg_dump, no raw audio required):

```bash
mkdir -p backups
docker compose --env-file operator/.env -f compose.operator.yaml exec -T db pg_dump -U echo -d echo_operator -Fc > backups/operator.dump
```

On Windows, avoid binary redirection through older PowerShell. Use a container
file and copy it out:

```powershell
docker compose --env-file operator/.env -f compose.operator.yaml exec db pg_dump -U echo -d echo_operator -Fc -f /tmp/operator.dump
$DbContainer = docker compose --env-file operator/.env -f compose.operator.yaml ps -q db
docker cp "${DbContainer}:/tmp/operator.dump" ./operator.dump
```

Restore to an isolated stack/volume first. Stop API and workers to prevent new
writes, copy the dump into the target DB container, and run:

```bash
docker compose --env-file operator/.env -f compose.operator.yaml stop gateway echo-rtsp-worker vmt-camera-emulator
docker compose --env-file operator/.env -f compose.operator.yaml exec -T db pg_restore -U echo -d echo_operator --clean --if-exists --no-owner /tmp/operator.dump
docker compose --env-file operator/.env -f compose.operator.yaml up -d
```

The restore command replaces the **target** DB's objects. Only run it against the
intended recovery target after preserving that target's data. Verify migration
hashes, source/site memberships, lifecycle receipts, audit history and pending
outbox before reconnecting operators. Stale pending notifications expire; a
crash after provider acceptance but before DB commit can retry the same browser
tag. Exactly-once device delivery is not claimed.

Rollback application code to a compatible Git/image SHA. The initial migration
has no destructive automatic down migration. A future incompatible schema
change requires its own migration/rollback decision; do not edit applied SQL.

## 6. Optional VPS configuration (NOT DEPLOYED)

Use only after independent runtime/security review and deployment authorization.
The local path remains usable without a VPS. Choose a user-controlled host,
configure DNS yourself, use HTTPS PUBLIC_ORIGIN and OPERATOR_DOMAIN, and set
OPERATOR_MODE=production. Lab push is forcibly disabled in the override.

```bash
docker compose --env-file operator/.env -f compose.operator.yaml -f compose.operator.vps.yaml up -d --build
```

Only Caddy ports 80/443 are public; DB, broker, RTSP, HLS and gateway have no host
ports. Private broker traffic is trusted only inside this dedicated Docker
network; no anonymous public MQTT listener is authorized. Off-host Acoustic
Plane connectivity requires a separately reviewed authenticated TLS/private
network adapter and secret management. Do not expose the existing professor
demo or emulator control server directly to the internet.

The Compose file colocates the lab by default. A small VPS is not assumed to run
PANNs inference adequately. Separate-plane topology is an architectural option,
not an implemented deployment or a measured capacity promise.

## 7. Observability / stop

`/api/health` requires a session and reports DB connectivity, MQTT state, live
source count and SSE clients. Each source exposes worker snapshot age and
estimated window-end-to-snapshot lag. These are diagnostics, not certified SLOs.
Quarantine stores payload hash/topic/reason/count, not arbitrary raw messages.
Audit records include controls, acknowledgement, resolution and account changes.

```bash
docker compose --env-file operator/.env -f compose.operator.yaml logs --tail=100 gateway broker db
docker compose --env-file operator/.env -f compose.operator.yaml down
```

Do not use `down -v` unless deliberately deleting persistent state. No audio
recording is enabled. DB/event/audit retention is currently manual and unbounded
on disk; define and validate a site-specific retention/purge policy before any
public/field operation. Container logs rotate; broker queues and packet sizes
are bounded. No automatic paid fallback exists.
