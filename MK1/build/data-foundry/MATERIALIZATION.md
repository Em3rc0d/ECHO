# MK1 Dataset Materialization

**Status:** `EXECUTION_PREPARED / FULL_MEDIA_REQUIRES_PERSISTENT_STORAGE`

ECHO does not call a dataset “materialized” merely because a source URL or class count exists. A source is materialized only when its real bytes are present on controlled storage, publisher identity/checksums are verified where available, and every admitted asset passes the Data Foundry chain.

## Corpus objective

The frozen MK1 taxonomy is:

```text
GLASS_SHATTER
SIREN
FIRE_ALARM
VEHICLE_HORN
TIRE_SQUEAL
```

The materialization plan is versioned in:

```text
configs/data_foundry/materialization_plan.v1.json
```

Exact-gap candidate discovery lives in:

```text
configs/data_foundry/gap_source_candidates.v1.json
```

## Source families

```text
Publisher corpora
  SONYC-UST v2.3
  FSD50K v1.0
  SINGA:PURA v1.0a
  ESC-50
  UrbanSound8K 1.0

Gap-closing sources
  FreesoundDataset exact Fire alarm / Tire squeal candidate pools
  BigSoundBank CC0 exact alarm / tire-squeal recordings
  MIVIA Road AED (research-only semantic candidate for tire-skidding -> reviewed TIRE_SQUEAL)

Augmentation/reference only
  ShantyCam synthetic smoke alarms
  AudioSet ontology/annotations

Field
  ECHO Field Dataset — untouched holdout after authorization
```

No synthetic dataset receives independent-real-source credit. AudioSet raw media is not auto-ingested. Broad labels such as generic alarm, generic screeching or friction brake cannot silently close an exact target gap.

## Hosted CI vs full-media execution

Ordinary hosted CI materializes only small publisher metadata, checksum evidence and exact-gap candidate identities. This is deliberate: the selected publisher archives are tens of gigabytes and full extraction needs persistent storage substantially larger than hosted-runner scratch space.

`MK1 Dataset Metadata Materialization` therefore produces committed evidence snapshots under:

```text
MK1/mining-site/materialization/
```

Full-media execution requires a persistent self-hosted data node with at least **120 GiB free** before starting. The raw bytes stay outside Git. Only manifests, hashes, reports, reviews and certification evidence belong in the repository.

## Full-media stop line

A source is not corpus-ready until:

```text
publisher bundle / upstream asset
        ↓
real bytes acquired
        ↓
publisher checksum where available
        ↓
SHA-256 per local asset
        ↓
audio probe
        ↓
license/use decision
        ↓
exact semantic mapping/manual review
        ↓
recording/uploader/site grouping
        ↓
exact + near duplicate audit
        ↓
deterministic group-aware split
        ↓
coverage/diversity/hard-negative gate
```

The only accepted terminal condition for a release-safe corpus is:

```text
coverage-gate.json.status == PASS
coverage-gate.json.gap_codes == []
CERT-MK1-DF-CORPUS-001 == CERTIFIED
```

Anything else remains open.

## FIRE_ALARM and TIRE_SQUEAL

These classes are no longer treated as “unknown source” problems. Public exact-label candidate pools have been identified. They remain **media-execution and review** problems:

- FreesoundDataset exposes 87 Fire alarm candidates / 24 ground-truth examples and 23 Tire squeal candidates / 10 ground-truth examples.
- Additional CC0 recordings are tracked from BigSoundBank to provide a second independently governed source family.
- MIVIA Road AED contributes a research candidate pool for tire-skidding, but only event segments that audibly satisfy ECHO `TIRE_SQUEAL` may pass manual review.

Candidate counts are never admitted counts.

## Operational next step

`EXEC-DATA-001` now means running the versioned materializer on persistent storage, completing all manual/authorized source acquisitions, and feeding every resulting asset through the existing Foundry. No model benchmark may bypass this corpus certificate.
