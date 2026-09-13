# MK0 Certificate

```yaml
certificate_id: CERT-MK0-013
project: ECHO
milestone: MK0
status: CERTIFIED
issued_at: 2026-09-13
promise: "Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial"
scope:
  - research evidence
  - problem/scope boundary
  - dataset/model landscape
  - source/streaming architecture
  - event lifecycle
  - pubsub decision
  - MK1 taxonomy
  - benchmark protocol
  - privacy requirements
excludes:
  - empirical model winner
  - thresholds
  - real-camera compatibility
  - measured distance
  - measured latency
  - final SLOs
external_gates:
  - EXT-CAMERA-001
owner_legal_gate:
  - ECHO source-code license
```

## Inputs

- `PROJECT-CHARTER.md`
- `MK0/mining-site/WEB-AUDIT-2026-09-13.md`
- `research/MODEL-MATRIX.md`
- `research/DATASET-MATRIX.md`
- `research/RELATED-PROJECTS.md`
- `MK1/design/TAXONOMY.md`
- `MK1/plan/BENCHMARK-PROTOCOL.md`
- `governance/DECISION-LOG.md`
- `governance/RISK-REGISTER.md`
- `governance/PRIVACY-COMPLIANCE.md`

## Validation rule

This certificate is valid only while the exact upstream artifacts remain semantically compatible. Git history supplies immutable versions; future CI should compute SHA-256 for each input and generate a machine-readable attestation manifest.

## Next certificate

`CERT-MK1-READY-001` authorizes **starting** the replay/offline MK1 build. It does not claim the build exists or passes tests.