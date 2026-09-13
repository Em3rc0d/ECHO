# Quarry — Security Operations

**Status:** operational control framework `CERTIFIED_FOR_MK2_DESIGN`; implementation evidence required before release.

## 1. Purpose

Turn MK0 threat modeling into day-2 controls: credentials rotate, dependencies change, logs accumulate and incidents happen.

## 2. Identity and secrets

Production profile should provide:

```text
unique service/client identities
least-privilege broker/API ACLs
secret store or protected environment injection
rotation procedure
revocation procedure
no credentials in image/repo/logs
```

## 3. Network operations

Prefer segmentation between camera network, ECHO compute and user-facing services. Public exposure of RTSP/ONVIF management endpoints is not an ECHO requirement.

Document allowed flows explicitly.

## 4. Patch/dependency management

Maintain software bill of materials where feasible and track:

```text
OS/base image
FFmpeg/runtime
ML framework
broker
API dependencies
model/checkpoint hashes
```

Security upgrades trigger regression tests when they can affect codec/inference behavior.

## 5. Logging and audit

Logs should contain enough identifiers for incident reconstruction without leaking secrets/raw conversations:

```text
source_id
service/version
connection/error category
event_id
model/config version
auth/security outcome
```

Credentials and raw RTSP URLs are redacted.

## 6. Abuse/spoof considerations

A replayed sound can trigger an acoustic detector. ECHO should document this as spoofability of the sensor modality. High-consequence downstream actions should require corroboration or human confirmation according to product policy.

## 7. Backup/recovery

Back up configuration, schemas, certification manifests and event metadata according to deployment requirements. Raw continuous audio is not part of normal backup because it is not retained by default.

## 8. Incident scenarios

Playbooks should cover:

- leaked camera/broker credential;
- compromised source identity;
- anomalous event flood;
- repeated worker crash;
- corrupted/tampered model artifact;
- unauthorized subscriber;
- event-store loss/corruption.

## 9. Release security evidence

Before MK2 release certification:

- secrets scan clean;
- dependency/SBOM inventory generated;
- ACL/auth tests pass;
- artifact hashes/signatures/provenance verified according to chosen tooling;
- malformed input/failure isolation tests pass;
- incident/rollback procedure tested.
