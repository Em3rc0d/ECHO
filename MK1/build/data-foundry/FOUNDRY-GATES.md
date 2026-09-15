# MK1 Data Foundry — Gates and Closure Criteria

**Status:** `TOOLCHAIN_RECERTIFICATION_REQUIRED / SONYC_CERTIFIED / CORPUS_CLOSURE_ACTIVE`  
**Toolchain:** `CERT-MK1-DF-TOOLCHAIN-005 = CANDIDATE`  
**SONYC:** `CERT-MK1-DF-SONYC-001 = CERTIFIED`  
**Corpus:** `CERT-MK1-DF-CORPUS-001 = OPEN`  
**Readiness:** `EMP-MK1-CORPUS-READINESS-001 = BLOCKED`  
**Global invariant:** `ECHO-FREE-TIER-001`

## Gate chain

```text
DF-G0 source registry
  -> DF-G1 provenance/acquisition
  -> DF-G2 rights
  -> DF-G3 exact semantics / governed hard negatives
  -> DF-G4 real-byte integrity + probe + canonical fingerprint
  -> corpus-role boundary
  -> DF-G5 global dedup + acoustic recording-family closure
  -> DF-G6 group-aware split / conflict quarantine
  -> coverage/diversity/hard-negative solidity
  -> DF-G7 freeze #1 -> clean freeze #2 -> reproducibility
  -> EMP-DATASET-001 + EMP-DATA-QUALITY-001
  -> CERT-MK1-DF-CORPUS-001
  -> DF-G8 model-entry
```

No downstream gate compensates for an upstream failure. No paid fallback, label coercion, wrapper double-counting, synthetic source independence, duplicate-family inflation, seed shopping or floor reduction is permitted.

## Certified SONYC node

```text
CERT-MK1-DF-SONYC-001 = CERTIFIED
implementation baseline   ab8c47ba6aabb25390644954a2a06945ca7a81bb
SONYC run                  34922010537
verified shards            19/19 PASS
probe/fingerprint failures 0 / 0
durable evidence           78fc019839f1c9dad1a58a70d439605d887361d7
```

This node is scoped to SONYC materialization/fingerprint closure only.

## Corpus-role boundary — PASS

Review-only materializations without an exact positive or governed hard-negative role are excluded from the corpus-facing ledger while source evidence is retained.

```text
input rows                 1164
retained corpus-role rows  1081
review-only removed          83
canonical fingerprints     1081/1081
```

## DF-G2 / DF-G3 — three row blockers remain

```text
LICENSE_NOT_RELEASE_SAFE = 1
SEMANTIC_STATUS_CONFLICT_FIRE_ALARM = 1
SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL = 1
```

They must be resolved from exact source evidence or excluded from corpus membership. No positive/HN credit may be coerced.

## DF-G5 — PASS

Post-grouping empirical chain:

```text
PR #11 merge                8c547b70d23ce6c592ddd20d55ff37df9fa7fa03
canonical ledger            9fa3d2f90ddfb731d0921749c921ab2987d54307
closure evidence            e3e0f58dee3a1602e92f62c8a7708fa1e9fad9ea
readiness                   8e7702a2bf629642f78859763dabbe09df03df02
```

Global grouping facts:

```text
fallback assets before              448
fallback assets after                 0
global acoustic components           17
members reassigned                    97
screened fallback groups             357
cross-source-group near edges        831
content merged/deleted              false
```

Closure results:

```text
global-dedup-audit.json       PASS / gap_codes=[]
recording-family-audit.json   PASS / gap_codes=[]
missing groups                0
pending global group audits   0
```

Acoustic fingerprint proximity is used for shared split protection, not as proof that two source objects are identical.

## DF-G6 — FAIL, exact next blocker

```text
split-integrity.json = FAIL
original_split_conflict_count = 3
eligible_asset_count = 1078
UNASSIGNED = 62
```

Conflicting components:

```text
global-acoustic:49755af077645d9cd379
global-acoustic:683a2c690a388e66903b
global-acoustic:b0a528766144425812e3
```

The safe resolution is deterministic whole-component quarantine from development/final corpus membership whenever one acoustic component contains incompatible protected original splits. Source evidence remains retained. Moving individual clips, choosing a favorable seed, or splitting the acoustic component is forbidden.

## Corpus solidity — frozen

`MK1-CORPUS-SOLIDITY-001` remains unchanged.

Per target:

```text
assets >= 50
groups >= 25
underlying sources >= 2
duration >= 180 s
largest source fraction <= 0.80
train >= 20 assets / 10 groups
validation >= 5 assets / 3 groups
test >= 5 assets / 3 groups
```

Per-target hard negatives require `>=20 assets / >=10 groups / >=2 underlying sources`. Global background/negatives require `>=200 assets / >=50 groups / >=3 underlying sources`.

## Current final coverage failures

Measured after grouping:

```text
FIRE_ALARM    9 assets / 6 groups; train 7/4, validation 2/2, test 0/0
TIRE_SQUEAL  11 assets / 11 groups; train 9/9, validation 0/0, test 2/2
GLASS_SHATTER largest source fraction 0.976974 > 0.80
BACKGROUND    1 underlying source < 3
```

Hard-negative deficits:

```text
FIRE_ALARM       26 assets / 26 groups / 1 source
GLASS_SHATTER   342 assets / 341 groups / 1 source
SIREN            26 assets / 26 groups / 1 source
TIRE_SQUEAL       0 assets / 0 groups / 0 sources
VEHICLE_HORN      0 assets / 0 groups / 0 sources
```

Therefore coverage requires real-media acquisition from genuinely independent acoustic source families. More Freesound wrappers do not create a second FREESOUND family.

## Current readiness

At `8e7702a2bf629642f78859763dabbe09df03df02`:

```text
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = fcd07c11d3291d5a78ee28cae93e42de0f16e78522720e78fffb5e71b4bcf129
```

Current readiness has 20 gap codes. Global dedup, grouping, and canonical fingerprint coverage are no longer among them. Remaining categories are: corpus cert absent; coverage not PASS; three ledger rights/semantic blockers; split not PASS; FIRE_ALARM/TIRE_SQUEAL asset deficits; HN source/asset deficits; freeze #1/#2 and reproducibility not PASS.

## DF-G7 — freeze/reproducibility

Freeze #1/#2 are ineligible while upstream split/coverage fails. Once eligible, both must bind exact membership, media hashes, groups, splits, source/rights/mapping policies, dedup and coverage evidence. A second clean process build must reproduce the same semantic identity.

## DF-G8 — model entry

`build_corpus_closure_readiness.py --require-modeling-ready` must remain non-zero until `CERT-MK1-DF-CORPUS-001` is certified, every required closure node is PASS and `gap_codes=[]`.

No Benchmark A/B/C, model training, threshold calibration, replay progression or real-camera progression is authorized before that transition.

## Certificate lineage

```text
CERT-MK1-DF-SPEC-001        CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004   INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005   CANDIDATE
CERT-MK1-DF-SONYC-001       CERTIFIED / scoped
EMP-DATASET-001              OPEN
EMP-DATA-QUALITY-001         OPEN
CERT-MK1-DF-CORPUS-001      OPEN
```

## Invalidation

Any material change to taxonomy, source/acquisition, rights/mapping/review, probing/fingerprints, grouping/dedup, split/coverage/freeze/handoff semantics, readiness/model-entry guard, SONYC evidence, tests/schemas/workflows, governing documentation or `ECHO-FREE-TIER-001` requires dependency review and selective recertification.
