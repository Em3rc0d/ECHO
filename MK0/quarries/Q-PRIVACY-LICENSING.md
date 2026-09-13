# Quarry — Privacy, Data Governance and Licensing

**Status:** baseline policy `CERTIFIED`; site-specific legal authorization and final source-code license remain separate gates.

## 1. Privacy design

Default runtime flow:

```text
continuous audio
 -> bounded volatile buffer
 -> preprocessing/inference
 -> event metadata
 -> discard raw continuous audio by default
```

The goal is data minimization: ECHO needs acoustic features/events, not a permanent archive of ambient conversations.

## 2. Explicit exclusions

Core ECHO does not require:

```text
speech transcription
speaker identification
voice biometrics
conversation-content analysis
```

Adding one of those later would require a new privacy/scope review and cannot be smuggled into the existing promise as an implementation detail.

## 3. Evidence clips

If evaluation/debugging requires storing short clips, the capture protocol must define:

```text
purpose
authorization
who can access
retention period
storage location
encryption/access controls where applicable
redaction/deletion process
link to event/experiment id
```

No default “store everything in case it is useful later”.

## 4. Field dataset governance

A field recording manifest includes consent/authorization reference as appropriate to the deployment context, collection purpose, site/device metadata, retention status and whether the asset may be used for training, testing or only transient debugging.

Local legal compliance is an external/site gate. Engineering documentation does not substitute for legal review.

## 5. Licensing layers

Always separate:

1. ECHO-owned source-code license;
2. third-party library license;
3. pretrained model/checkpoint license;
4. dataset release license;
5. individual audio-asset license;
6. media/service terms that may govern access/redistribution.

“Free”, “open source” and “publicly downloadable” are not interchangeable.

## 6. Dataset examples

- ESC-50 full dataset is distributed under CC BY-NC; its smaller ESC-10 subset has different terms documented by the project.
- FSD50K contains mixed per-clip licenses and therefore requires asset-level filtering/recording.
- AudioSet metadata/ontology licensing does not automatically grant rights to redistribute underlying YouTube media.

Exact license text/release is the source of truth at ingestion time.

## 7. THIRD_PARTY registry

Before distributable release ECHO should generate/maintain a registry with:

```text
component/asset
version/release
source URL
license SPDX/name
copyright/attribution
redistribution requirements
checkpoint/data-specific conditions
hash
```

## 8. Source-code license

The license for ECHO-owned code remains a repository-owner decision. Apache-2.0 is a candidate, not silently assumed. This does not block internal engineering but blocks a clean public release claim until closed.

## 9. Data deletion and reproducibility tension

Reproducibility prefers immutable data; privacy/licensing may require deletion. Resolve by keeping manifests/hashes/provenance even if the actual asset cannot be retained. A missing/revoked asset is marked unavailable rather than silently replaced under the same identity.

## 10. Closure conditions

The architecture-level privacy/licensing policy is closed. Re-open if ECHO adds speech/identity processing, continuous recording, new datasets with incompatible terms, cloud transfer of raw audio, or a new distribution model.
