# Quarry — Privacy and Licensing

**Status:** `DESIGN_POLICY_CERTIFIED / FIELD_AND_RELEASE_GATES_OPEN`

## Privacy baseline

ECHO fulfills its promise without understanding speech content or identity. Default pipeline:

```text
continuous audio
 -> short bounded in-memory buffer
 -> features/inference/event decision
 -> discard raw samples
```

`ASR_CONTINUOUS`, speaker identification and voice profiling remain off. Field/evidence clips require explicit purpose, permission, retention and ACL.

## Privacy risks

Incidental conversations, excessive retention, reuse of field data for training without authorization, raw audio in debug/crash files, credentials in URLs/logs and broad access to camera streams.

## Controls

Metadata-first storage, retention off, temp-file audits, access minimization, secrets external to Git, data manifests with permitted use and separate field-holdout/training permissions.

## Licensing layers

```text
ECHO source code license
third-party library/binary license
model architecture code license
checkpoint license
pretraining/data terms
dataset release license
individual asset license
```

Never collapse these into “open source”. FSD50K's per-clip licensing illustrates why asset-level governance matters. AudioSet metadata/ontology terms do not grant automatic redistribution rights to underlying YouTube media.

## Release gate

Exact dependency/checkpoint/data BOM, notices, hashes and permitted-use records required before distributable release. ECHO-owned license remains an explicit owner decision.

## Field gate

Real capture requires authorization and documented purpose/access/retention; project engineering controls do not replace legal/institutional review.

## Invalidation

New jurisdiction, cloud media processing, ASR/speaker features, persistent clips or a new restricted dependency reopens this quarry.