# MK1 Data Foundry — Admission, Rights and Provenance Policy

**Status:** `FROZEN_FOR_MK1`

## 1. Goal

Ensure every training/evaluation asset has sufficient identity, rights, semantic and quality evidence for its declared use profile. Downloadability is not admission.

## 2. Admission states

```text
DISCOVERED
  -> STAGED
  -> ADMITTED_RELEASE_SAFE | ADMITTED_RESEARCH_ONLY | ADMITTED_FIELD_HOLDOUT
  -> QUARANTINED
  -> REJECTED
```

`QUARANTINED` means evidence may be resolved later. `REJECTED` means the current asset/version cannot be used under the requested profile.

## 3. Mandatory asset evidence

An admitted record must contain, when available/applicable:

- stable ECHO `asset_id`;
- source dataset and release;
- upstream asset/file ID;
- canonical origin URI or release reference;
- local content SHA-256;
- byte size and audio technical metadata once probed;
- exact asset license/terms or inherited dataset terms when genuinely uniform;
- permitted-use classification;
- original labels;
- ECHO labels and mapping relation;
- label provenance/annotation quality metadata;
- recording/source/uploader/site/device group identity;
- original split plus ECHO split;
- field-holdout flag;
- admission/rejection/quarantine reasons.

## 4. License decision profile

The default profile is deliberately conservative because ECHO may evolve beyond a university-only experiment.

| Terms | Default decision | Rationale |
|---|---|---|
| CC0 / public-domain-equivalent evidence | `ALLOW_RELEASE_SAFE` | permissive, attribution normally not required but provenance retained |
| CC BY 4.0 / compatible attribution license | `ALLOW_RELEASE_SAFE` | attribution/provenance required |
| CC BY-SA 4.0 | `REVIEW_REQUIRED` | ShareAlike implications must be understood for intended distribution/model-data artifacts |
| CC BY-NC / other non-commercial | `RESEARCH_ONLY` | can be useful for academic experiments but must not contaminate release-safe lineage |
| CC Sampling+ | `REVIEW_REQUIRED` | special terms require asset/use-specific review |
| unknown/custom/incomplete | `QUARANTINE` | no assumption from availability |
| explicitly incompatible/prohibited | `DENY` | do not ingest into declared use profile |

This is engineering governance, not legal advice. If a release/use scenario changes, rights are re-reviewed.

## 5. FSD50K special rule

FSD50K has a dataset-level CC-BY curation license while individual audio clips carry distinct Creative Commons licenses. ECHO records **both** levels and bases audio use on the individual clip terms. Dataset-level CC-BY does not erase per-asset restrictions.

Default `release_safe` policy admits only clips classified `ALLOW_RELEASE_SAFE`; NC/Sampling+ clips remain outside that profile.

## 6. NC datasets

ESC-50 and UrbanSound8K are useful scientific references, but their full datasets are non-commercial. They remain isolated in `research_extended` experiments. A model trained on them is not represented as having release-safe provenance unless a later rights analysis explicitly permits the intended use.

## 7. ShareAlike datasets

SINGA:PURA is CC BY-SA 4.0. The data is scientifically valuable, especially for strong urban labels, but the Foundry marks it `REVIEW_REQUIRED` for release-safe lineage until obligations for the intended artifact/distribution are resolved. Research experiments may use a separately tagged profile where permitted.

## 8. AudioSet rule

AudioSet ontology/annotations can be referenced, and pretrained models may have their own independently reviewed licenses. The raw underlying YouTube-derived media is excluded from automatic ECHO acquisition. A video/segment ID does not prove stable availability, redistribution rights, or permission for ECHO storage.

## 9. Field data

Field assets require:

- explicit authorized collection context;
- source/device/site pseudonymous IDs;
- purpose and permitted use;
- retention policy;
- privacy/access classification;
- whether clip is holdout-only, training-eligible later, or prohibited from persistence.

Continuous audio is not retained by default merely because Foundry can process files.

## 10. Provenance immutability

Raw upstream releases are treated as immutable. If upstream data is corrected or replaced, ECHO creates a new source/release identity and re-hashes the local assets. Historical manifests remain reproducible.

## 11. Attribution inventory

For every admitted attribution-bearing asset/source, the Foundry emits an attribution inventory containing creator/source/license identifiers and any required notice text/reference. Release tooling consumes this inventory; attribution is not reconstructed manually at the end.

## 12. Quarantine reasons

Canonical reason codes include:

```text
LICENSE_UNKNOWN
LICENSE_RESEARCH_ONLY_FOR_REQUESTED_PROFILE
LICENSE_REVIEW_REQUIRED
PROVENANCE_MISSING
HASH_MISSING
LABEL_MAPPING_AMBIGUOUS
LABEL_REVIEW_REQUIRED
QUALITY_INVALID
DUPLICATE_CONFLICT
GROUP_ID_UNKNOWN_FOR_PROTECTED_SPLIT
FIELD_PERMISSION_MISSING
PRIVACY_RESTRICTION
```

## 13. Validation

The machine policy is in `configs/data_foundry/license_policy.v1.json`. Unit tests lock classification behavior. Generated reports must show admitted/quarantined/rejected counts by source and reason.

## 14. Invalidation

A license/terms correction, intended-use change, redistribution strategy change, or provenance correction creates a new policy/manifest identity and requires downstream lineage review.