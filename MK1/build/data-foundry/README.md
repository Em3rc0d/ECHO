# MK1 Data Foundry

**Status:** `BUILD_IN_PROGRESS / CORE_SPEC_FROZEN / CORPUS_NOT_YET_ADMITTED`

## 1. Purpose

The MK1 Data Foundry is the build-time layer that converts heterogeneous public, sensor-network and future ECHO field audio into a **traceable, versioned, license-aware and leakage-resistant corpus**. It lives inside `MK1/build`; it is not a new milestone phase and does not alter the frozen flow `brainstorming -> design -> arch -> plan -> build -> test`.

The Foundry exists because model quality cannot be certified if the data path is informal. A clip is not usable merely because it can be downloaded or because its source label resembles an ECHO label.

## 2. Contract

Every admitted asset must be reconstructible through:

```text
source release
  -> upstream asset identity
  -> origin/provenance
  -> exact license/use decision
  -> content hash
  -> original labels
  -> semantic mapping decision
  -> group identity
  -> quality/dedup evidence
  -> split assignment
  -> frozen manifest identity
```

If any mandatory link is missing, the asset is `QUARANTINED` or `REJECTED`; it does not silently enter training.

## 3. Data zones

```text
EXTERNAL / LANDING
  immutable downloaded release or authorized field capture
        |
        v
STAGING
  source-specific metadata parsed to RawAssetCandidate
        |
        v
QUARANTINE <---- license/provenance/mapping/quality uncertainty
        |
        v
CURATED
  hashed + mapped + grouped + deduplicated assets
        |
        +--> TRAIN
        +--> VALIDATION
        +--> TEST
        +--> FIELD_HOLDOUT  (never used for fitting/calibration)
```

Large audio is not committed to Git. Git stores code, schemas, registries, manifests, hashes, reports and certification evidence. Raw media stays in governed local/object storage according to its license and privacy constraints.

## 4. Frozen taxonomy input

MK1 v1 targets are:

- `GLASS_SHATTER`
- `SIREN`
- `FIRE_ALARM`
- `VEHICLE_HORN`
- `TIRE_SQUEAL`

`BACKGROUND_NO_TARGET` is a data state; `UNKNOWN` is a decision-layer abstention state and is not automatically a training class.

## 5. Source strategy

The Foundry intentionally combines sources by role rather than pretending one dataset covers ECHO:

- **FSD50K 1.0** — broad permissive/mixed-license source pool; strong for `Shatter`, `Siren`, `Vehicle horn`; asset-level license filtering is mandatory.
- **SONYC-UST v2** — real urban sensor domain; exact `car-horn` and `siren`, multilabel context and hard negatives.
- **SINGA:PURA v1.0a** — strongly labelled urban sensor audio; includes `Glass breaking`, `Car horn`, `Siren` and temporal onset/offset; ShareAlike implications require release-policy review.
- **ESC-50** — small sanity benchmark with `Siren` and `Car horn`; full dataset is non-commercial and therefore research-only for ECHO's default release-safe profile.
- **UrbanSound8K** — urban contrast with `car_horn` and `siren`; non-commercial, research-only.
- **AudioSet** — ontology/pretraining/reference metadata. Raw YouTube-derived media is not admitted by default because metadata availability does not grant ECHO redistribution/training rights for each underlying item.
- **ECHO Field Dataset** — future authorized camera/microphone evidence and holdout; gated by `EXT-CAMERA-001` and privacy/permission controls.

## 6. Important data gaps

`FACT/EVIDENCE`: no currently selected release-safe source gives ECHO a sufficient, clean, directly ingestible pool for both `FIRE_ALARM` and `TIRE_SQUEAL`.

Therefore these two classes are **not fabricated from broader labels**. The Foundry records them as coverage gaps to be solved through a permissively licensed source, controlled/synthetic generation validated against real examples, and/or authorized ECHO field collection. A generic `Alarm`, `Screech`, `Brake` or `Friction brake` label is not promoted to these targets without semantic evidence.

## 7. Build outputs

The Foundry build produces:

```text
source registry
license policy
label mapping registry
asset manifest JSONL
split manifest
quarantine/rejection report
dedup report
class/source/license coverage report
manifest SHA-256
field-holdout manifest (when available)
```

These identities become inputs to the MK1 model benchmark. A benchmark without the exact Foundry manifest/split hashes is non-certifiable.

## 8. Implementation

Runtime-independent Foundry code lives in `src/echo/data_foundry/`. Machine-readable policies live in `configs/data_foundry/`; schemas live in `schemas/data_foundry/`; tests live in `tests/data_foundry/`.

The implementation intentionally starts with deterministic metadata/provenance/split logic before decoding audio or training a neural network.

## 9. Stop-the-line conditions

Stop downstream corpus construction when any of the following is detected:

- unknown/incompatible license or missing attribution provenance;
- same physical/source group crossing protected splits;
- duplicate/near-duplicate leakage across test boundary;
- broad/ambiguous label being automatically treated as an exact target;
- field holdout consumed by training, threshold tuning or error-driven augmentation;
- mutable manifest without new version/hash;
- data report that cannot reproduce its asset population.

## 10. Certification boundary

The Foundry architecture/policies can be certified before the corpus exists. **Exact admitted counts, durations, class balance, duplicate findings and final data sufficiency remain empirical outputs** until the source releases are acquired and the pipeline is executed.

See the other files in this folder for source evidence, semantic mappings, admission policy, split/dedup design, hard negatives, field holdout, runbook and gates.