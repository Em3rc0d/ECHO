# Quarry — Security Threat Model

**Status:** baseline controls `CERTIFIED_FOR_MK1`; production hardening continues in MK2.

## 1. Assets

Protect:

```text
camera/NVR credentials
broker credentials
API credentials
source registry
model/checkpoint artifacts
configuration
field audio/evidence clips
event history
certification manifests
logs/telemetry
```

## 2. Trust boundaries

```text
camera network -> ingest adapter
ingest process -> inference service
inference -> Event Engine
Event Engine -> broker
broker -> subscribers
CI/repository -> deployment/model artifacts
```

Each boundary must define authenticated identity, accepted input shape and failure behavior appropriate to the deployment stage.

## 3. Threats

### Credential disclosure

Secrets accidentally committed, printed in RTSP URLs or leaked in process logs.

Controls: environment/secret store injection, URL redaction, `.gitignore`, no credentials in fixtures.

### Source impersonation

A malicious or misconfigured publisher claims another `source_id`.

Controls: source registry, broker ACLs/identities, validate source identity at adapter boundary.

### Audio spoof/replay

A speaker can replay a target sound. ECHO detects acoustics and cannot claim the physical cause is genuine from audio alone. This is a documented limitation, not something the classifier silently “solves”. Downstream systems may corroborate with video/sensors.

### Command/path injection

Unsafe construction of FFmpeg shell commands from user/vendor strings can execute unintended shell syntax.

Control: structured subprocess arguments, avoid shell execution, validate paths/options, constrain adapter config.

### Malformed streams/payloads

Unexpected codecs, corrupt packets or malformed MQTT/HTTP payloads can crash parsers.

Controls: process isolation, timeouts, schema validation, bounded buffers, restart policy.

### Supply-chain tampering

Model/checkpoint/dependency content can change upstream.

Controls: pin versions, checksum downloaded artifacts, provenance manifest, later signatures/attestations.

## 4. Network stance

PoC may operate on an isolated trusted lab LAN, but that is an explicit deployment assumption. It must not be generalized to production.

Production design should consider network segmentation, least-privilege routing, broker/API TLS where feasible and no direct public exposure of camera management ports.

## 5. Broker controls

At minimum beyond local dev:

```text
authentication
ACLs by client/topic
unique identities
secret rotation
connection/audit logs
rate/size limits where supported
```

## 6. Data security

Continuous audio is not stored by default. Any approved evidence clip receives access control, retention and provenance. Event metadata can still be sensitive operational data and should not be treated as public by default.

## 7. Availability threats

- reconnect storm;
- queue exhaustion;
- broker outage;
- intentionally noisy audio causing excessive inference/event load;
- disk/log exhaustion;
- model worker crash loop.

Controls are bounded queues, backoff, rate/volume observability and independent source supervision.

## 8. Security test requirements

- verify secrets absent from repo/log samples;
- malformed source config rejected;
- invalid event payload rejected;
- unauthorized MQTT topic publication denied in hardened profile;
- checkpoint hash mismatch fails closed;
- one source failure cannot crash all sources;
- replayed duplicate event is idempotently handled downstream.

## 9. Non-claims

ECHO does not authenticate that a sound came from a real-world event rather than playback, does not identify speakers and does not infer a crime from sound. Those boundaries must remain visible in product/documentation language.
