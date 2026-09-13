# Data Foundry Architecture — MK1

**Status:** `FROZEN_FOR_IMPLEMENTATION`

## 1. Architectural objective

Build one deterministic path from heterogeneous upstream releases to a benchmark-ready ECHO corpus without coupling model code to dataset-specific formats.

```text
Public dataset / field source
          |
          v
+----------------------+       +----------------------+
| Source Adapter       |-----> | RawAssetCandidate    |
+----------------------+       +----------------------+
                                      |
                                      v
                            +----------------------+
                            | Provenance + license |
                            +----------------------+
                                      |
                             reject/quarantine?
                               /            \
                              v              v
                       QUARANTINE        continue
                                             |
                                             v
                                   +----------------+
                                   | Content hash   |
                                   +----------------+
                                             |
                                             v
                                   +----------------+
                                   | Label mapping  |
                                   +----------------+
                                             |
                                    manual review?
                                      /       \
                                     v         v
                              QUARANTINE    continue
                                                |
                                                v
                                    +-------------------+
                                    | Quality + dedup   |
                                    +-------------------+
                                                |
                                                v
                                    +-------------------+
                                    | Group assignment  |
                                    +-------------------+
                                                |
                                                v
                                    +-------------------+
                                    | Split planner     |
                                    +-------------------+
                                                |
                                                v
                                    +-------------------+
                                    | Frozen manifests  |
                                    +-------------------+
                                                |
                       +------------------------+-----------------------+
                       |                        |                       |
                       v                        v                       v
                    TRAIN                 VALIDATION                 TEST
                                                                       \
                                                                        +--> FIELD_HOLDOUT
```

## 2. Boundary rule

Source adapters may know upstream column names and directory structure. Everything after `RawAssetCandidate` uses ECHO contracts only. Benchmark/model code consumes frozen manifests, never raw dataset-specific CSVs directly.

This isolates upstream release changes from the ML/runtime layer and makes provenance auditable.

## 3. Components

### 3.1 Source registry

Machine-readable inventory of approved/candidate releases. It records source identity, official URL/DOI, release, license model, data role, target coverage and restrictions. It is policy input, not proof that every asset is admissible.

### 3.2 Source adapters

Parsers normalize metadata from FSD50K, SONYC-UST, SINGA:PURA, ESC-50, UrbanSound8K and future ECHO field manifests. Adapters must not decide final ECHO semantics by string similarity.

### 3.3 Provenance/license gate

Produces a license decision for the intended ECHO profile:

`ALLOW_RELEASE_SAFE`, `RESEARCH_ONLY`, `REVIEW_REQUIRED`, `QUARANTINE`, `DENY`.

The default product-safe corpus does not silently import NC/restricted assets merely because the current university experiment could technically use them.

### 3.4 Hash/integrity layer

Computes SHA-256 over local audio bytes after acquisition. Source-provided MD5/SHA checksums are also retained as upstream evidence, but ECHO uses its own SHA-256 for asset identity.

### 3.5 Semantic mapping

Maps source labels to ECHO taxonomy with explicit relation: `EXACT`, `NARROWER`, `BROADER`, `AMBIGUOUS`, `NEGATIVE`, `UNUSABLE`. `BROADER`/`AMBIGUOUS` mappings cannot become positive targets without clip-level review or stronger metadata.

### 3.6 Quality and dedup

Checks required metadata, readable/valid duration information once audio probing is enabled, impossible timestamps, zero-length assets and exact duplicate hashes. Near-duplicate/audio-fingerprint support is a later Foundry increment; until then, source/uploader/group boundaries remain mandatory safeguards.

### 3.7 Grouping and split planner

The unit of separation is the most conservative known physical/source group, not the clip. Examples: Freesound original recording/uploader, UrbanSound `fsID`/occurrence, SONYC/SINGA sensor, field recording session/site/device.

Split assignment is deterministic for a frozen seed/config. No default ratio is hidden in code; the benchmark plan supplies the explicit split profile.

### 3.8 Manifest writer

Writes canonical, sorted JSONL plus a dataset-level manifest. Hashes are calculated from canonical serialization, making the corpus identity reproducible and comparable.

### 3.9 Reports

Required reports include target support, independent group counts, duration, license distribution, quarantine/rejection reasons, mapping status, source diversity, split leakage audit, duplicate audit and hard-negative coverage.

## 4. Storage architecture

Recommended local layout; directory names are operational, not Git-tracked data:

```text
data/
  external/          # immutable acquired upstream releases
  staging/           # adapter outputs / temporary normalized metadata
  quarantine/        # unresolved rights/semantics/quality
  curated/           # admitted assets or links/references
  field/             # authorized ECHO field capture
  manifests/         # frozen JSONL + dataset/split manifests
  reports/           # generated statistics/audits
  cache/             # disposable derived cache
```

`data/external`, `data/curated`, `data/field` and caches must remain outside Git or be ignored. Manifests/reports can be committed when they contain no sensitive/raw-media content.

## 5. Dataset profiles

A single manifest may expose multiple policy profiles without duplicating audio:

- `release_safe`: permissive/approved assets only.
- `research_extended`: may include non-commercial research datasets when the experiment is explicitly academic and outputs are not used to claim release-safe training provenance.
- `field_holdout`: authorized real-domain data isolated from training/calibration.

Every result names its profile; metrics from `research_extended` cannot silently certify a `release_safe` model.

## 6. Failure behavior

Foundry defaults to fail closed on unknown rights, mapping ambiguity affecting positive labels, split overlap or missing identity fields. Batch execution may continue processing independent assets, but the final manifest is not certified if mandatory gates fail.

## 7. Reproducibility identity

A corpus identity is at minimum:

```text
taxonomy_version
source_registry_hash
license_policy_hash
label_mapping_hash
admission_config_hash
split_policy_hash
asset_manifest_hash
split_manifest_hash
```

The MK1 build manifest later references these hashes alongside model/config identities.

## 8. Downstream consumers

- replay source and audio window pipeline;
- A/B/C model benchmark;
- threshold calibration;
- hard-negative mining;
- Event Engine validation;
- field evaluation;
- certification ledger.

A material change in any Foundry identity invalidates downstream benchmark comparability until re-run.