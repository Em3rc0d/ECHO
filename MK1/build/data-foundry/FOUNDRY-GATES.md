# MK1 Data Foundry — Gates and Closure Criteria

**Status:** `TOOLCHAIN_IMPLEMENTED / REAL_CORPUS_EXECUTION_PENDING_SOURCE_MEDIA`

## 1. Gate chain

```text
DF-G0 source registry frozen
  -> DF-G1 source release/provenance verified
  -> DF-G2 rights profile classified
  -> DF-G3 semantic mapping/review complete
  -> DF-G4 content integrity + quality checked
  -> DF-G5 grouping + duplicate audit complete
  -> DF-G6 split/holdout audit complete
  -> DF-G7 manifest/report bundle frozen
  -> DF-G8 benchmark handoff accepted
```

A downstream gate cannot certify around a failed upstream gate. The software path for G0-G8 is implemented; a named real corpus instance is certified only after external media/metadata is acquired and run through the chain.

## 2. DF-G0 — Source registry

PASS when each selected source has stable ID/release/canonical evidence URL, license model, intended role and target coverage limitations. `configs/data_foundry/source_registry.v1.json` is the semantic registry; `acquisition_registry.v1.json` records release bundles/checksums where publishers expose them.

## 3. DF-G1 — Acquisition/provenance

PASS per source when acquired files correspond to the declared release and upstream checksums/metadata are retained where available. `echo-data-foundry acquisition-plan` exposes expected bundles and `verify-acquisition` checks local copies. Local audio identity is calculated independently with SHA-256.

## 4. DF-G2 — Rights

PASS when every admitted asset has a policy decision compatible with the requested profile. `release_safe` contains no silent `RESEARCH_ONLY`, `REVIEW_REQUIRED` or unknown-license assets. Unknown terms fail closed.

## 5. DF-G3 — Mapping and review

PASS when all positive labels are supported by `EXACT`/approved narrower mapping or documented asset-level review. `BROADER`/`AMBIGUOUS` positive candidates cannot bypass `echo.review-decisions.v1`. Review cannot override rights or provenance gates.

Target-level gaps are allowed only when explicitly reported; fake semantic coverage is not.

## 6. DF-G4 — Integrity/quality

PASS when all admitted assets exist, hash successfully and satisfy enabled technical checks. Missing/corrupt files do not enter the admitted manifest. Candidate/asset identities are deterministic and source-specific parser behavior is unit-tested.

## 7. DF-G5 — Groups/dedup

PASS when every protected-evaluation asset has a defensible group ID, one group maps to one protected split, exact duplicate SHA-256 content does not cross boundaries and any registered near-duplicate fingerprint does not cross boundaries.

A lightweight PCM-WAV normalized-envelope fingerprint helper is implemented for near-duplicate screening. Unsupported formats can inject an equivalent decoder-derived fingerprint into the same record field; SHA-256 remains canonical identity.

## 8. DF-G6 — Splits/holdout

PASS when group overlap = 0, exact/registered-near-duplicate overlap = 0 and field holdout overlap = 0 across prohibited boundaries. Recognized upstream train/validation/test semantics are preserved; otherwise the versioned split policy uses deterministic group hashing. Seed/profile/policy hash are recorded.

## 9. DF-G7 — Frozen bundle

PASS when the following exist and are mutually consistent:

```text
asset-manifest.jsonl
split-manifest.json
dataset-manifest.json
coverage-report.json
dedup-report.json
quarantine-report.json
```

The dataset manifest binds source registry, rights policy, label mapping, split policy, asset manifest and split manifest hashes. A second execution over unchanged inputs must reproduce the component identities.

## 10. DF-G8 — Benchmark handoff

PASS when MK1 benchmark configuration references exact Foundry data identities and enumerates train/validation/test exclusively from the frozen bundle. Manual directory selection is a FAIL.

## 11. Implemented execution surface

```text
acquisition-plan / verify-acquisition
        ↓
intake spec -> candidate JSONL
        ↓
admit -> hash + license + mapping + review -> record JSONL
        ↓
freeze -> split + duplicate audit + reports + dataset manifest
        ↓
benchmark handoff
```

These operations are covered by unit and synthetic end-to-end CI. Real multi-gigabyte public media is deliberately not downloaded in GitHub CI.

## 12. Target coverage health

Foundry reports each target from the actual admitted manifest. Before real corpus execution, historical research indicates `SIREN` and `VEHICLE_HORN` have the strongest source diversity, `GLASS_SHATTER` has direct plus reviewable candidates, and `FIRE_ALARM`/`TIRE_SQUEAL` require defensible direct assets for the release-safe profile. This is a sourcing statement, not a model-performance result.

## 13. Certificate plan

- `CERT-MK1-DF-SPEC-001`: Foundry architecture/contracts/policies/code foundation — certified.
- `CERT-MK1-DF-TOOLCHAIN-001`: acquisition→intake→admission→review→split/dedup→freeze toolchain — emitted after CI for the completed implementation.
- `EMP-DATASET-001`: actual admitted corpus identity/counts — produced only from real source execution.
- `EMP-DATA-QUALITY-001`: real duplicate/quality/source-diversity findings — produced only from real source execution.
- `CERT-MK1-DF-CORPUS-001`: emitted only after G0..G8 PASS for a named real profile/manifest.

Changes to taxonomy, mapping, rights policy, grouping/split rules, adapters or source release invalidate dependent Foundry/benchmark evidence and require re-run rather than silent patching.
