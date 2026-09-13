# MK2 Security Architecture

**Status:** `DESIGN_SPECIFIED / THREAT PROFILE DEPLOYMENT-SPECIFIC`

## Trust zones

Source camera/NVR network, ECHO ingest/runtime, model/artifact store, broker/event store, observability and operator/admin interfaces are distinct trust zones.

## Identity and secrets

Per-service/source credentials where practical, least privilege, external secret manager/environment integration, rotation and revocation. Never derive authorization only from payload `source_id`.

## Transport

Use TLS/VPN/network segmentation where components cross untrusted boundaries. Legacy RTSP without strong transport protection should be confined to trusted/segmented network or secure tunnel according to deployment.

## Broker

Authenticated clients and ACL topic scope. Publisher identity must not spoof arbitrary source/site. Audit auth failures/config changes.

## Supply chain

SBOM, pinned dependencies/native binaries, model/checkpoint hashes/provenance, container/base image inventory and optional signed attestations/release artifacts.

## Runtime hardening

Non-root where feasible, minimal filesystem/network permissions, constrained subprocess invocation, resource limits and no arbitrary shell execution from configuration.

## Data security

Encrypt sensitive persistent evidence as deployment requires, control access to optional audio clips and observability metadata, enforce retention/deletion.

## Incident readiness

Credential/model/dependency compromise has documented revoke/rollback/rotate path.

## Validation

Threat review, config/ACL tests, secret scanning, dependency/image scan, artifact signature/hash verification and fault/abuse tests before production certification.