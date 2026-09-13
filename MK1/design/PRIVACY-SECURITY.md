# Privacy and Security Design — MK1

**Status:** `FROZEN_BASELINE / FIELD_GATE_EXTERNAL`

## Privacy invariants

No continuous ASR, speaker identification or voice profiling. Continuous raw audio retention off by default. Event/health metadata is preferred over media. Field clips require explicit authorized evaluation purpose and manifest permissions.

## Secrets

RTSP/broker credentials are supplied through environment/secret references. Config stores secret names, not values. Logs redact URIs/userinfo and exceptions must not dump secret-bearing command lines.

## Adapter safety

Construct FFmpeg/GStreamer arguments as structured arguments; avoid shell interpolation of untrusted source/config strings. Restrict file paths/URLs to configured schemes/policies.

## Model supply chain

Checkpoints/dependencies record origin/version/hash. Do not execute arbitrary downloaded model code in privileged context without provenance review.

## Broker security

Local PoC may run within a controlled environment, but field use requires authentication and topic ACLs; TLS/network segmentation depends on deployment threat model.

## Data-at-rest

If benchmark/field clips are stored, access, retention and permitted use are explicit. Temp files/crash dumps are part of privacy tests.

## Threats explicitly not solved in MK1

Acoustic anti-spoofing/replay authenticity, enterprise IAM, full vulnerability management and distributed secrets rotation are deferred unless external requirements demand them.

## Validation

Secret scan, log inspection, unauthorized broker tests, invalid model checksum, no-retention filesystem audit and field authorization checklist.

## Invalidation

Cloud upload, persistent evidence clips, ASR/speaker features or public-network deployment requires new threat/privacy review.