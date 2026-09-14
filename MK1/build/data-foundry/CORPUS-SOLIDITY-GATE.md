# MK1 Corpus Solidity Gate

**Status:** `ENFORCED_FOR_RELEASE_SAFE_FREEZE`  
**Policy:** `MK1-CORPUS-SOLIDITY-001`  
**Global invariant:** `ECHO-FREE-TIER-001`

The MK1 corpus is not considered certified merely because every target label appears once. A release-safe ECHO corpus must pass a versioned, fail-closed coverage, diversity, leakage and evidence gate before it can be handed to the benchmark.

## Certification floor

For every frozen target class:

- at least **50 admitted assets**;
- at least **25 independent recording groups**;
- at least **2 independent underlying source datasets/families**;
- at least **180 s of positive clip exposure**;
- train: at least **20 assets / 10 groups**;
- validation: at least **5 assets / 3 groups**;
- test: at least **5 assets / 3 groups**;
- no single underlying source may contribute more than **80%** of one class.

The development corpus must also contain at least **200 background/hard-negative assets**, **50 independent negative groups**, and **3 negative sources**.

Per target, explicit hard-negative coverage must satisfy the configured policy floor of at least **20 assets / 10 groups / 2 sources**.

These values are a **minimum engineering certification floor**, not a claim that this amount of data guarantees a particular F1, recall, PR-AUC or deployment result. Model sufficiency remains empirical and is decided by the benchmark.

## Independence semantics

The following quantities are not interchangeable:

```text
asset count
!=
independent recording-family count
!=
independent underlying-source count
```

A dataset wrapper does not create a new acoustic source.

Example:

```text
FSD50K metadata points to Freesound sound X
+
direct Freesound acquisition of sound X

=> one underlying recording family
=> one underlying source-family credit
=> never two-source diversity credit
```

One original recording segmented into multiple clips remains one group for independence accounting unless evidence proves distinct underlying captures.

## Hard rules

```text
field_holdout != development coverage
synthetic augmentation != independent source
broad/ambiguous label != exact target coverage
one duplicated recording != multiple independent groups
metadata row != real-byte corpus credit
AudioSet annotation != redistribution right to underlying media
FSD50K wrapper + same Freesound asset != two sources
quarantined asset != coverage credit
```

The field holdout is excluded from development coverage calculations. It may validate domain behavior later but may never be used to hide a train/validation/test gap.

## Release-safe admission prerequisite

An asset can contribute to solidity counts only after all required evidence is closed:

```text
real bytes observed
+ source/release provenance
+ release-safe rights decision
+ semantic mapping/review PASS
+ SHA-256 identity
+ technical audio probe PASS
+ positive duration
+ recording-family identity
+ label provenance
+ dedup/near-dup evidence
```

If any mandatory item is missing, the asset is excluded from release-safe coverage credit.

## Near-duplicate prerequisite

Final corpus certification requires cross-format/transcode-aware near-duplicate screening for admitted assets.

A byte hash alone is insufficient for transformed copies. The near-duplicate policy must canonical-decode audio locally and validate its similarity rule against known duplicate transformations and known-independent fixtures before the policy version is frozen.

Cross-split exact, near-duplicate or recording-family leakage must be zero.

## FIRE_ALARM / TIRE_SQUEAL

These labels remain the highest-risk data nodes. The gap-closing plan is deliberately multi-source:

```text
exact Freesound/public candidates
        +
other individually licensed exact public assets where provenance is defensible
        +
future authorized ECHO controlled-development recordings where policy allows
        ↓
manual semantic review when required
        ↓
per-asset rights decision
        ↓
SHA-256 + audio probe
        ↓
recording-family + dedup
        ↓
group-aware split
        ↓
coverage policy
```

`AudioSet` remains useful as ontology/pretraining/coverage evidence, but its annotation count does not automatically authorize acquisition or redistribution of the underlying media.

A separate `ECHO Field Dataset` stays untouched as holdout and does not count toward the 50/25/2 development floor.

## Split floor rule

The deterministic group-aware split must itself satisfy the configured per-class split floors.

If the frozen split policy produces an insufficient validation/test distribution, the correct response is **not** to move clips manually or change seeds until the split passes.

Instead:

```text
current split policy fails
        ↓
certificate remains OPEN
        ↓
version a deterministic whole-group constrained allocator
        ↓
rerun complete split / leakage / coverage evidence
```

## Free-tier interaction

A zero-gap target does not supersede `ECHO-FREE-TIER-001`.

If a coverage node cannot be closed inside the zero-cost boundary:

```text
keep the node OPEN
or EXTERNAL_GATE_OPEN
```

Do not lower this solidity floor, buy infrastructure, enable overages or treat research-only evidence as release-safe merely to obtain PASS.

## Stop line

A release-safe freeze with any unmet rule returns:

```text
FAIL_COVERAGE_GATE
```

and its frozen bundle is not eligible for benchmark handoff or `CERT-MK1-DF-CORPUS-001`.

The exact machine-readable policy lives in:

`configs/data_foundry/coverage_policy.v1.json`

The complete closure sequence lives in:

`MK1/build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md`
