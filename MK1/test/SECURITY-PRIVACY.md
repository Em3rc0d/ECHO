# MK1 Security and Privacy Tests

**Status:** `SPECIFIED`

## Secrets

Repository secret scan; effective config/log inspection; RTSP/MQTT URLs must not reveal credentials. Invalid-secret errors should be actionable without echoing secret values.

## Adapter injection

Test malicious/invalid URL/path/config characters against structured FFmpeg invocation; no shell command injection or arbitrary path use.

## Broker authorization

In field-like config, unauthorized client cannot publish as another source or subscribe to restricted topics. Authentication failure is logged safely.

## Model integrity

Checkpoint hash mismatch fails closed before inference. Model provenance/version is included in result bundle.

## Raw audio retention

Run replay/live path and inspect configured output/temp/crash locations. No continuous PCM/WAV remains by default after normal operation. Any optional evidence clip feature is disabled unless explicit policy.

## Data permissions

Manifest prevents training use for assets marked holdout/research-only/incompatible. Field holdout remains excluded.

## Resource/DoS baseline

Malformed/stalled source and reconnect storm do not create unbounded queues/processes.

## Scope

These are MK1 controls, not a full penetration test. MK2 expands production network/IAM/supply-chain/incident security.