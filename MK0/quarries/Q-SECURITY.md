# Quarry — Security

**Status:** `BASELINE_CERTIFIED / PRODUCTION_HARDENING_MK2`

## Assets and trust boundaries

Camera/NVR credentials, broker credentials, stream URIs, model/checkpoint files, configuration, logs, event store and optional field audio clips are security-sensitive. The source network and third-party model/data supply chain are separate trust boundaries.

## Threats

Credential leakage in Git/logs/process arguments, unauthorized RTSP access, MQTT publisher spoofing, command/path injection in FFmpeg adapters, tampered model/checkpoint, malformed media/decoder attack surface, replayed audio, excessive privileges and denial-of-service through unbounded queues/reconnect storms.

## MK1 controls

Secrets via environment/secret references; sanitize RTSP URLs; fixed argument construction rather than shell concatenation; checksum/provenance model artifacts; bounded resources; broker auth/ACL for field use; least-privilege filesystem/network; explicit source_id authorization mapping; no raw media in logs.

## Replay/spoofing boundary

A loudspeaker replay is still an acoustic signal and may trigger a classifier. Anti-spoof/source-authenticity is a separate research problem unless the product later requires it. ECHO must document this limitation rather than implying authenticity.

## Tests

Secret scan, log redaction, invalid credentials, unauthorized publish/subscribe, malformed config, model checksum mismatch, adapter argument injection cases, reconnect storm and resource exhaustion.

## MK2 hardening

TLS/network segmentation as deployment requires, container/service isolation, SBOM, signed provenance, vulnerability/dependency process, rotation/incident procedures and stricter broker ACLs.

## Invalidation

Cloud deployment, public-network exposure, new media retention or remote model-update mechanisms expand the threat model and require recertification.