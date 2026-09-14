# MK1 Data Foundry — Gates and Closure Criteria

**Status:** `TOOLCHAIN_IMPLEMENTED / REAL_CORPUS_CLOSURE_ACTIVE`  
**Global invariant:** `ECHO-FREE-TIER-001`  
**Closure plan:** `CORPUS-FOUNDRY-CLOSURE-PLAN.md`

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

A downstream gate cannot certify around a failed upstream gate. The software path for G0-G8 is implemented; a named real corpus instance is certified only after actual release-safe asset evidence passes the full chain.

All gates inherit `ECHO-FREE-TIER-001`. Capacity or source constraints never authorize a paid fallback, quality-threshold reduction or fabricated closure.

## 2. DF-G0 — Source registry

PASS when each selected source has stable ID/release/canonical evidence URL, license model, intended role and target-coverage limitations.

`configs/data_foundry/source_registry.v1.json` is the semantic registry; `acquisition_registry.v1.json` records release bundles/checksums where publishers expose them.

Underlying-source independence is stricter than dataset-wrapper identity. If an FSD50K asset and a direct Freesound asset resolve to the same underlying Freesound sound, they belong to one acoustic source/recording family for diversity accounting.

## 3. DF-G1 — Acquisition / provenance

PASS per source when acquired files correspond to the declared release and upstream checksums/metadata are retained where available.

`echo-data-foundry acquisition-plan` exposes expected bundles and `verify-acquisition` checks local copies. Local audio identity is calculated independently with SHA-256.

Metadata-only knowledge does not count as release-safe real-byte corpus coverage.

## 4. DF-G2 — Rights

PASS when every admitted asset has a policy decision compatible with the requested profile.

`release_safe` contains no silent `RESEARCH_ONLY`, `REVIEW_REQUIRED` or unknown-license assets. Unknown or incompatible terms fail closed.

Rights uncertainty can never be solved by semantic review.

## 5. DF-G3 — Mapping and review

PASS when all positive labels are supported by `EXACT`/approved narrower mapping or documented asset-level review.

`BROADER`/`AMBIGUOUS` positive candidates cannot bypass versioned review evidence. Review cannot override rights or provenance gates.

Frozen semantic stop-lines include:

```text
Alarm     != FIRE_ALARM
Squeak    != TIRE_SQUEAL
Car       != VEHICLE_HORN
Glassware != GLASS_SHATTER
```

Target-level gaps remain visible until direct evidence closes them.

Hard-negative mappings are never re-labelled as target positives.

## 6. DF-G4 — Integrity / technical quality

PASS when all admitted assets:

```text
exist as real observed bytes during materialization/admission
hash successfully
have positive byte size
contain a valid audio stream
have positive duration
carry source + label provenance
satisfy enabled technical checks
```

Missing/corrupt/unprobeable files do not enter the admitted manifest.

Candidate/asset identities are deterministic and source-specific parser behavior is unit-tested.

## 7. DF-G5 — Groups / dedup

PASS when every protected-evaluation asset has a defensible recording-family identity, one family maps to one protected split, exact duplicate SHA-256 content does not cross boundaries and registered near-duplicates do not cross boundaries.

The strongest known grouping relationship wins:

```text
physical event / continuous session
  > original recording
  > source/uploader + occurrence
  > sensor/site/time block
  > clip id only when no stronger relationship exists
```

### Near-duplicate hardening requirement

The existing lightweight fingerprint implementation is not sufficient by itself for final corpus certification because format/transcode coverage can be incomplete.

Before `CERT-MK1-DF-CORPUS-001`, all admitted audio formats must be canonical-decoded locally into a deterministic mono 16 kHz signed-16-bit PCM stream for fingerprint/vector generation. The canonical PCM does not need to persist.

The final proximity threshold must be validated by deterministic transformed-copy and known-independent fixtures before its policy version is frozen.

PASS requires:

```text
expected transformed duplicates detected
AND
known-independent fixtures not declared duplicates
```

## 8. DF-G6 — Splits / holdout

PASS when:

```text
group overlap = 0
exact duplicate overlap = 0
registered near-duplicate overlap = 0
field holdout overlap = 0
```

Recognized upstream train/validation/test semantics are preserved where required; otherwise the versioned split policy uses deterministic group assignment.

Current `split_policy.v1` remains valid if the resulting real corpus also passes per-class split floors.

If v1 fails those floors, do not move clips manually and do not seed-shop. Design a versioned deterministic whole-group constrained allocator (`split_policy.v2`) and rerun the full split evidence.

## 9. Coverage and diversity gate

`MK1-CORPUS-SOLIDITY-001` is an engineering certification floor, not a model-performance guarantee.

A release-safe corpus must meet the configured floors for:

```text
positive assets / class
independent recording groups / class
underlying independent sources / class
positive duration / class
train / validation / test floors
largest-source fraction
background / hard-negative population
hard negatives per target
technical quality
license provenance
label provenance
exact/near-duplicate violations
```

Field holdout, synthetic augmentation, broad labels and repeated segments of one recording cannot be used to manufacture independent coverage.

## 10. Hard-negative execution gate

A hard-negative mapping is policy input, not materialized evidence.

Hard-negative coverage receives credit only after:

```text
real bytes
+ source provenance
+ release-safe rights
+ valid probe
+ recording family
+ exact dedup
+ near-duplicate screening
+ explicit hard_negative_for
```

A dedicated bounded execution/reporting surface must close this node before corpus certification.

## 11. DF-G7 — Frozen bundle

PASS when the following exist and are mutually consistent:

```text
asset-manifest.jsonl
split-manifest.json
dataset-manifest.json
coverage-report.json
coverage-gate.json
dedup-report.json
quarantine-report.json
```

The dataset manifest binds source registry, rights policy, label mapping, split policy, asset manifest and split manifest identities.

## 12. Reproducibility sub-gate

A second clean freeze over unchanged admitted data/policies must reproduce the semantic corpus identity:

```text
same asset membership
same asset SHA-256 identities
same recording-family assignments
same split membership
same dedup decisions
same coverage result
same gap_codes
```

Volatile timestamps may differ only when explicitly excluded from corpus identity.

## 13. DF-G8 — Benchmark handoff

PASS when MK1 benchmark configuration references the exact validated Foundry bundle identity and enumerates train/validation/test exclusively from that bundle.

Manual directory selection is a FAIL.

## 14. Implemented execution surface

```text
acquisition-plan / verify-acquisition
        ↓
intake spec -> candidate JSONL
        ↓
admit -> hash + license + mapping + review -> record JSONL
        ↓
freeze -> split + duplicate audit + reports + dataset manifest
        ↓
validate-bundle / list-split
        ↓
benchmark handoff
```

Real materialization is already active through bounded source-specific workflows. Raw multi-gigabyte corpora remain outside Git/artifact persistence by design.

## 15. Explicit open nodes before corpus certification

At the time of this update, the following remain closure-critical and must not be hidden:

```text
OPEN: canonical cross-format near-duplicate hardening + fixture validation
OPEN: dedicated hard-negative materialization/evidence integration
OPEN: final global corpus-closure integration workflow/evidence packet
OPEN until empirical PASS: final global rights/semantic/dedup/group/split/coverage audit
```

These are implementation/evidence gaps, not reasons to reopen the frozen taxonomy or project promise.

## 16. Certificate plan

- `CERT-MK1-DF-SPEC-001`: Foundry architecture/contracts/policies/code foundation — certified.
- `CERT-MK1-DF-TOOLCHAIN-001`: acquisition→intake→admission→review→split/dedup→freeze toolchain — toolchain evidence.
- `EMP-DATASET-001`: actual admitted corpus identity/counts — real source execution only.
- `EMP-DATA-QUALITY-001`: real duplicate/quality/source-diversity findings — real source execution only.
- `CERT-MK1-DF-CORPUS-001`: emitted only after G0..G8 plus reproducibility and free-tier boundary PASS for a named real profile/manifest.

Changes to taxonomy, mapping, rights policy, grouping/split rules, adapters, source release or free-tier execution policy invalidate dependent Foundry/benchmark evidence and require rerun rather than silent patching.
