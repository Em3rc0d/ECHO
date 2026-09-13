# Quarry — Security Operations

**Status:** `DESIGN_READY / DEPLOYMENT-SPECIFIC CONTROLS PENDING`

## Objective

Move from MK1 secure coding/config baseline to ongoing production security operations.

## Workstreams

Credential issuance/rotation/revocation; broker/source ACL review; dependency/container/model vulnerability and provenance checks; patch/update process; audit/log retention; incident response; backup/recovery of non-audio state; access review for evidence clips/field data.

## Model supply chain

Verify checkpoint digest/provenance before activation; control who may promote model/config; retain signed/hashable release manifest; rollback compromised artifact.

## Device reality

Some cameras have weak/legacy security. Compensating controls can include network segmentation, VPN/tunnel, restricted service accounts and preventing direct public exposure.

## Detection

Monitor auth failures, unexpected source/publisher identities, configuration changes, repeated reconnect anomalies, checksum failures and unusual resource patterns without ingesting unnecessary personal data.

## Incident drills

Secret compromise, malicious/incorrect model artifact, unauthorized MQTT publisher and vulnerable dependency each need a response path.

## Release gate

Security operations requirements are profile-specific but must be documented/tested before claiming production readiness.