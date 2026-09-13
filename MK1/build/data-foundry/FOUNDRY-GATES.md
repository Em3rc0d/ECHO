# MK1 Data Foundry — Gates and Closure Criteria

**Status:** `GATES_DEFINED / EXECUTION_OPEN`

## 1. Gate chain

```text
DF-G0 source registry frozen
  -> DF-G1 source release/provenance verified
  -> DF-G2 rights profile classified
  -> DF-G3 semantic mapping complete
  -> DF-G4 content integrity + quality checked
  -> DF-G5 grouping + duplicate audit complete
  -> DF-G6 split/holdout audit complete
  -> DF-G7 manifest/report bundle frozen
  -> DF-G8 benchmark handoff accepted
```

A downstream gate cannot certify around a failed upstream gate.

## 2. DF-G0 — Source registry

PASS when each selected source has stable ID/release/canonical evidence URL, license model, intended role and target coverage limitations. Sources with unresolved release identity cannot be used in a certified manifest.

## 3. DF-G1 — Acquisition/provenance

PASS per source when acquired files correspond to the declared release and upstream checksums/metadata are retained where available. Local content identity is calculated independently with SHA-256.

## 4. DF-G2 — Rights

PASS when every admitted asset has a policy decision compatible with the requested profile. `release_safe` contains no silent `RESEARCH_ONLY`, `REVIEW_REQUIRED` or unknown-license assets.

## 5. DF-G3 — Mapping

PASS when all positive labels are supported by `EXACT`/approved `NARROWER` mapping or documented clip-level review. `BROADER`/`AMBIGUOUS` labels cannot bypass review.

Target-level gaps are allowed if explicitly reported; fake semantic coverage is not.

## 6. DF-G4 — Integrity/quality

PASS when all admitted assets exist, hash successfully and satisfy the enabled technical quality checks. Corrupt/missing files are absent from admitted manifest and present in a rejection report.

## 7. DF-G5 — Groups/dedup

PASS when every protected-evaluation asset has a defensible group ID, exact duplicates are resolved, label conflicts are reviewed and no known related group is split across protected boundaries.

Near-duplicate detection becomes a stronger gate once its implementation is available; its absence must remain a known limitation rather than implied coverage.

## 8. DF-G6 — Splits/holdout

PASS when group overlap = 0, exact-hash overlap = 0 and field holdout overlap = 0 across prohibited boundaries. Split seed/profile is recorded and deterministic.

## 9. DF-G7 — Frozen bundle

PASS when asset/split manifests, policy/mapping/source-registry hashes and generated reports exist and a second execution over unchanged inputs reproduces the canonical manifest digest.

## 10. DF-G8 — Benchmark handoff

PASS when MK1 benchmark config references exact data identities and can enumerate its train/validation/test assets exclusively from the Foundry bundle. Manual file selection is a FAIL.

## 11. Target coverage health

Foundry reports each target as:

```text
GREEN  = direct semantically valid source(s), adequate independent evidence pending measured sufficiency
AMBER  = evidence exists but rights/domain/count/diversity/review gap remains
RED    = no defensible direct training/evaluation pool yet
```

At Foundry start, `SIREN` and `VEHICLE_HORN` have the strongest source diversity; `GLASS_SHATTER` has direct SINGA evidence plus FSD review candidates; `FIRE_ALARM` and `TIRE_SQUEAL` remain acquisition gaps for the default release-safe profile.

No color becomes a quality claim until actual counts and benchmark results exist.

## 12. Certificate plan

- `CERT-MK1-DF-SPEC-001`: Foundry architecture/contracts/policies/code foundation reviewed and testable.
- `EMP-DATASET-001`: actual admitted corpus identity/counts; remains OPEN until execution.
- `EMP-DATA-QUALITY-001`: duplicate/quality/source-diversity findings; OPEN.
- `CERT-MK1-DF-CORPUS-001`: emitted only after DF-G0..G8 PASS for a named profile/manifest.

Changes to taxonomy, mapping, rights policy, grouping/split rules or source release invalidate dependent Foundry/benchmark certificates.