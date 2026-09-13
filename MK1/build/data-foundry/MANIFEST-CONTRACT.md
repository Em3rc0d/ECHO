# MK1 Data Foundry — Manifest Contract

**Status:** `FROZEN_V1`

## 1. Purpose

Define the canonical evidence record that separates ECHO training/evaluation from upstream dataset formats. Once a source adapter emits candidates, downstream Foundry stages and model benchmarks operate on this contract.

## 2. Asset record

Canonical fields:

```json
{
  "schema_version": "echo.asset-record.v1",
  "asset_id": "fsd50k-1.0:123456",
  "source_dataset": "fsd50k-1.0",
  "source_release": "1.0",
  "source_asset_id": "123456",
  "origin_uri": "...",
  "local_relpath": "external/fsd50k/...wav",
  "sha256": "...",
  "byte_size": 0,
  "duration_seconds": 0.0,
  "sample_rate_hz": 0,
  "channels": 0,
  "license_id": "CC-BY-4.0",
  "use_decision": "ALLOW_RELEASE_SAFE",
  "original_labels": ["Siren"],
  "echo_labels": ["SIREN"],
  "mapping_status": "EXACT",
  "label_provenance": "source_ground_truth",
  "recording_group_id": "...",
  "uploader_or_source_id": "...",
  "site_id": null,
  "device_id": null,
  "original_split": "dev",
  "echo_split": "train",
  "field_holdout": false,
  "admission_status": "ADMITTED_RELEASE_SAFE",
  "reason_codes": []
}
```

Optional unknown fields remain `null`; they are never silently synthesized. Fields mandatory for a specific gate are checked before admission/certification.

## 3. Identity rules

### `asset_id`

Stable within a source release and deterministic from `source_dataset + source_asset_id`. It is not a filesystem path.

### `sha256`

Identity of the exact acquired audio bytes. If upstream republishes different bytes under the same name, the hash change creates new evidence and invalidates the affected manifest.

### `recording_group_id`

Represents the strongest known leakage unit: original recording/event/session/uploader/sensor/field session. Split logic operates on groups, not clips.

## 4. Label rules

`original_labels` are preserved exactly enough to reconstruct source semantics. `echo_labels` are the mapped target set. `mapping_status` describes the strongest relation supporting positive use. Detailed per-label decisions can live in a mapping evidence sidecar when one clip contains multiple source labels with different relations.

`BACKGROUND_NO_TARGET` is represented by no positive ECHO target plus background/hard-negative metadata; it is not used to erase positive labels in polyphonic clips.

## 5. Dataset manifest

Dataset-level record:

```json
{
  "schema_version": "echo.dataset-manifest.v1",
  "manifest_id": "...",
  "created_at_utc": "...",
  "taxonomy_version": "echo.taxonomy.v1",
  "source_registry_sha256": "...",
  "license_policy_sha256": "...",
  "label_mapping_sha256": "...",
  "split_policy_sha256": "...",
  "asset_manifest_sha256": "...",
  "profile": "release_safe",
  "asset_count": 0,
  "source_releases": [],
  "known_gaps": [],
  "reports": {}
}
```

Counts are generated from the asset manifest, never hand-edited independently.

## 6. Split manifest

Contains one row per `recording_group_id` with assigned split, split-policy version/seed and any source-specific lock. Clip rows inherit the group split.

Field holdout uses a separate manifest/flag and cannot be reassigned by ordinary train/validation/test planning.

## 7. Canonical serialization

JSON objects are serialized with sorted keys and stable separators; JSONL asset rows are sorted by `asset_id` before final digest. This makes manifest hashes independent of filesystem enumeration order.

## 8. Sensitive data

Credentials, precise private location, unnecessary speech content/transcripts and unrestricted raw audio are never embedded in manifests. Field/site IDs are pseudonymous. `origin_uri` may be a dataset release reference rather than a private endpoint.

## 9. Versioning

Breaking field/semantic changes bump schema version. Data changes do not overwrite an old manifest; they produce a new `manifest_id` and digest.

## 10. Machine schemas

- `schemas/data_foundry/asset-record.schema.json`
- `schemas/data_foundry/dataset-manifest.schema.json`
- `schemas/data_foundry/source-registry.schema.json`

The Python dataclasses in `src/echo/data_foundry/contracts.py` implement the same conceptual boundary; JSON Schema remains the language-neutral artifact contract.