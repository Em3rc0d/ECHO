# MK1 Dataset Source Certification

**Status:** `SOURCE_CERTIFICATION_EXECUTION_OPEN`  
**Scope:** source/release identity, rights posture and reproducible publisher metadata evidence.  
**Not a claim:** this document does not certify the final ECHO audio corpus or any model metric.

## 1. Certification rule

A dataset name is not enough. ECHO treats a source as usable only after four independent questions are answered:

```text
identity/release
    + publisher provenance/checksums
    + rights/profile decision
    + semantic relevance
    = source-level admissibility
```

The concrete corpus still has to pass audio acquisition, SHA-256, per-asset rights where applicable, semantic mapping/review, technical probe, grouping, duplicate/near-duplicate screening, split isolation and frozen-manifest validation.

## 2. Source decisions

| Source | Exact release | Source evidence | `research_extended` | `release_safe` | Role |
|---|---|---|---|---|---|
| SONYC-UST | 2.3 | official Zenodo DOI/record + publisher MD5s | ALLOW | ALLOW | primary urban sensor source for `SIREN`, `VEHICLE_HORN`, hard negatives/context |
| FSD50K | 1.0 | official Zenodo DOI/record + publisher MD5s + per-clip license metadata | ALLOW | CONDITIONAL | broad curated pool; exact siren/horn, broader shatter requiring review |
| SINGA:PURA | 1.0a strongly-labelled subset | official Zenodo DOI/record + publisher MD5s | ALLOW | CONDITIONAL | strong temporal urban evidence for glass/siren/horn |
| ESC-50 | pinned snapshot required before corpus freeze | official upstream repository | ALLOW | DENY for full dataset | research sanity/contrast only |
| UrbanSound8K | 1.0 | official NYU distribution | ALLOW | DENY | research urban contrast only |
| AudioSet | ontology/annotations reference | Google research ontology | REFERENCE_ONLY | REFERENCE_ONLY | ontology/pretraining/coverage evidence, no raw-media auto-ingest |
| ECHO Field | future-v1 | project-owned evidence | DENY until authorization | DENY until authorization | untouched field holdout after external gates close |

Machine-readable source policy: `configs/data_foundry/dataset_certification.v1.json`.

## 3. Why FSD50K is conditional for release-safe lineage

The official FSD50K release states that clips carry their own Creative Commons licenses and publishes per-clip license metadata. The dataset entity itself is CC-BY, but the official record separately asks users interested in commercial use to contact the authors. ECHO therefore fails closed:

```text
research_extended -> allowed with per-asset rights checks
release_safe       -> CONDITIONAL until intended-use review is explicitly closed
```

This prevents a permissively licensed individual clip from silently overriding a source-level condition.

## 4. Why SINGA:PURA is conditional for release-safe lineage

The v1.0a strongly-labelled subset is CC-BY-SA-4.0. It is valuable because it supplies strongly labelled, polyphonic urban evidence and exact `Glass breaking`, `Siren` and `Car horn` classes. Research use is allowed under the project policy, but distributable model/product lineage remains conditional until ShareAlike implications for the intended artifact are explicitly reviewed.

## 5. Why SONYC-UST is the cleanest current primary source

SONYC-UST v2.3 is published under CC-BY-4.0 at the dataset level and comes from a real urban acoustic sensor network. It is therefore the cleanest current source-level fit for the default release-safe lineage, subject to attribution and all downstream Foundry gates.

It does **not** by itself cover all ECHO targets.

## 6. Publisher metadata checksum certification

Hosted CI certifies only small publisher metadata/control bundles, never the multi-gigabyte audio payloads. The workflow:

```text
.github/workflows/mk1-dataset-source-certification.yml
```

runs, for FSD50K, SONYC-UST and SINGA:PURA:

```text
publisher record
  -> deterministic file URL
  -> download metadata-stage bundle
  -> publisher MD5 verification
  -> independent SHA-256 computation
  -> source evidence JSON artifact
```

The full audio bundles are verified later by the same `acquisition_registry` against publisher MD5s and then every extracted asset receives its own SHA-256 inside the Foundry.

## 7. Stop-line source policy

`echo-data-foundry freeze` now receives the source certification policy. A frozen corpus fails if any admitted source is not `ALLOW` for the requested profile.

Examples:

```text
release_safe + SONYC-UST             -> allowed at source-policy layer
release_safe + FSD50K                -> STOP: CONDITIONAL
release_safe + ESC-50                -> STOP: DENY
research_extended + FSD50K/SINGA    -> allowed at source-policy layer
AudioSet raw-media source            -> STOP: REFERENCE_ONLY
ECHO field before authorization      -> STOP: EXTERNAL_GATE
```

Asset-level gates still run after source-level eligibility; `ALLOW` is necessary, never sufficient.

## 8. Coverage gap that remains explicit

The selected released corpora do not yet give a clean default source for both `FIRE_ALARM` and `TIRE_SQUEAL`. ECHO does not map generic alarm/screech/brake labels into those targets.

A separate quarry documents a defensible candidate path using legacy FreesoundDataset ground-truth pools plus per-asset license and semantic review. Until those assets are acquired and certified, these targets remain data gaps rather than fabricated coverage.

## 9. Certificates

Planned lineage:

```text
CERT-MK1-DF-SOURCE-POLICY-001
    source policy/config/code + tests

CERT-SRC-FSD50K-1.0
CERT-SRC-SONYC-UST-2.3
CERT-SRC-SINGAPURA-1.0A
    publisher metadata-stage checksum evidence

EXEC-DATA-001
    full real media acquisition/extraction/admission
        -> EMP-DATASET-001
        -> EMP-DATA-QUALITY-001
        -> CERT-MK1-DF-CORPUS-001
```

Source certificates prove release identity and publisher metadata integrity only. They never substitute for the final corpus certificate.
