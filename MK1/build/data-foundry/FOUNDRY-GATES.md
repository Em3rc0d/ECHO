# MK1 Data Foundry — Gates and Closure Criteria

**Status:** `TOOLCHAIN_RECERTIFICATION_REQUIRED / SONYC_CERTIFIED / REAL_CORPUS_CLOSURE_ACTIVE`  
**Current toolchain state:** `CERT-MK1-DF-TOOLCHAIN-005 = CANDIDATE`  
**Historical toolchain:** `CERT-MK1-DF-TOOLCHAIN-004 = INVALIDATED`  
**Current SONYC certificate:** `CERT-MK1-DF-SONYC-001 = CERTIFIED`  
**Current corpus readiness:** `EMP-MK1-CORPUS-READINESS-001 = BLOCKED`  
**Global invariant:** `ECHO-FREE-TIER-001`

## Gate chain

```text
DF-G0 source registry
  -> DF-G1 release/provenance
  -> DF-G2 rights
  -> DF-G3 exact semantics / governed hard-negative roles
  -> DF-G4 real-byte integrity + probe + canonical fingerprint
  -> corpus-role boundary
  -> DF-G5 global exact/near-duplicate + recording-family audit
  -> DF-G6 group-aware split / holdout audit
  -> coverage/diversity/hard-negative solidity
  -> DF-G7 freeze #1
  -> second clean freeze #2 + reproducibility
  -> EMP-DATASET-001 + EMP-DATA-QUALITY-001
  -> CERT-MK1-DF-CORPUS-001
  -> DF-G8 model-entry
```

No downstream gate can compensate for an upstream failure. All required execution inherits `ECHO-FREE-TIER-001`; paid fallbacks, synthetic source independence, label coercion and reduced floors are forbidden.

## Certified SONYC node

`CERT-MK1-DF-SONYC-001` remains independently valid and scope-bounded:

```text
implementation baseline  ab8c47ba6aabb25390644954a2a06945ca7a81bb
SONYC run                 34922010537
verified shards           19 / 19 PASS
probe failures            0
fingerprint failures      0
durable evidence          78fc019839f1c9dad1a58a70d439605d887361d7
```

It certifies SONYC v2.3 materialization/fingerprint closure only; it does not certify final corpus admission, grouping, split, coverage, freeze, model or field behavior.

## Corpus-role boundary — closed

PR #10 changed the corpus-facing ledger so materialized review candidates without an exact positive or governed hard-negative role no longer enter closure calculations. Source evidence is preserved.

Durable cascade:

```text
role-boundary merge       b2fc09b1c98c4c8adcb2fe9dc4db7e1dadc61107
canonical ledger evidence 3ba3f3141a24013abf8f3cbf68f46043a149ae12
closure audits            4ebbe3f042181ec789d26d1ff4d6ede4ba656ef9
closure readiness         ed069c64d8b5efc855157531a6a59aadff363f40
```

Current corpus-facing ledger truth before PR #11 grouping is applied:

```text
entry_count                         1081
canonical_fingerprint_count         1081
canonical_fingerprint_missing_count    0
role-boundary input_rows            1164
review-only rows removed              83
GROUPING_GLOBAL_AUDIT_REQUIRED       448
status = PASS_CONSOLIDATED_WITH_OPEN_GATES
```

The eliminated historical blockers were `AUGMENTATION_ONLY_NO_REAL_SOURCE_CREDIT`, `NO_EXACT_SEMANTIC_ROLE`, and `RIGHTS_TEXT_CONFLICT_REVIEW_REQUIRED`. They disappeared because those rows were not corpus roles, not because gates were weakened.

## DF-G2 / DF-G3 — remaining row-level blockers

Current fail-closed blockers that still require closure after grouping are:

```text
LICENSE_NOT_RELEASE_SAFE = 1
SEMANTIC_STATUS_CONFLICT_FIRE_ALARM = 1
SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL = 1
```

These must be resolved from source evidence or excluded from corpus credit; no label coercion is authorized.

## DF-G5 — global acoustic grouping / dedup

PR #11 is the active implementation change. Its rule is leakage protection, not content identity promotion:

- preserve existing source/curated groups;
- union exact media and canonical-PCM identity relations;
- union governed near-duplicate fingerprint relations into deterministic acoustic components;
- move fallback clips with no detected relation into explicitly screened singleton/source groups;
- remove `GROUPING_GLOBAL_AUDIT_REQUIRED` only after that deterministic global screen;
- never merge/delete audio or create new independent underlying-source credit;
- expose any original-split conflict to DF-G6 and fail closed.

Until PR #11 is merged and a fresh empirical cascade persists evidence, `global-dedup-audit.json` and `recording-family-audit.json` remain authoritative FAIL artifacts from the previous baseline.

## DF-G6 — split integrity

Group-aware splitting must prove:

```text
group overlap = 0
exact duplicate overlap = 0
near-duplicate leakage = 0
field holdout overlap = 0
original split conflict = 0
```

Seed shopping or per-clip movement to manufacture coverage is forbidden.

## Corpus solidity — unchanged

`MK1-CORPUS-SOLIDITY-001` remains frozen.

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

Per-target hard negatives: `>=20 assets / >=10 groups / >=2 underlying sources`. Global negatives: `>=200 assets / >=50 groups / >=3 underlying sources`.

Current pre-final positive assets / source families:

```text
FIRE_ALARM       10 / 3
GLASS_SHATTER   304 / 2
SIREN           175 / 3
TIRE_SQUEAL      11 / 2
VEHICLE_HORN    245 / 3
```

Current hard-negative assets / source families:

```text
FIRE_ALARM       34 / 1
GLASS_SHATTER   401 / 1
SIREN            32 / 1
TIRE_SQUEAL       0 / 0
VEHICLE_HORN      0 / 0
```

Therefore new real evidence is still required for FIRE_ALARM/TIRE_SQUEAL positive coverage and second-source hard negatives, especially TIRE_SQUEAL and VEHICLE_HORN. Existing source wrappers cannot be counted as independent acoustic families.

## Exact current readiness — pre-PR #11 cascade

`EMP-MK1-CORPUS-READINESS-001` at `ed069c64d8b5efc855157531a6a59aadff363f40` is `BLOCKED`, `eligible_for_certificate_review=false`, `modeling_allowed=false`, and `CERT-MK1-DF-CORPUS-001=OPEN`.

```text
CORPUS_CERTIFICATE_NOT_CERTIFIED
COVERAGE_GATE_GAP_CODES_NOT_EMPTY
COVERAGE_GATE_NOT_PASS
COVERAGE_GATE_STATUS_NOT_PASS
FIRE_ALARM_ASSETS_10_LT_50
FIRE_ALARM_HARD_NEGATIVE_SOURCES_1_LT_2
FREEZE_1_VALIDATION_NOT_PASS
FREEZE_2_VALIDATION_NOT_PASS
GLASS_SHATTER_HARD_NEGATIVE_SOURCES_1_LT_2
GLOBAL_DEDUP_AUDIT_NOT_PASS
LEDGER_GROUPING_GLOBAL_AUDIT_REQUIRED_448
LEDGER_LICENSE_NOT_RELEASE_SAFE_1
LEDGER_SEMANTIC_STATUS_CONFLICT_FIRE_ALARM_1
LEDGER_SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL_1
RECORDING_FAMILY_AUDIT_NOT_PASS
REPRODUCIBILITY_NOT_PASS
SIREN_HARD_NEGATIVE_SOURCES_1_LT_2
SPLIT_INTEGRITY_NOT_PASS
TIRE_SQUEAL_ASSETS_11_LT_50
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2
VEHICLE_HORN_HARD_NEGATIVES_0_LT_20
VEHICLE_HORN_HARD_NEGATIVE_SOURCES_0_LT_2
```

A fresh cascade after PR #11 supersedes this exact gap set and requires a new documentation audit.

## DF-G7 — freeze / reproducibility

Freeze #1 and #2 remain ineligible while any upstream gate fails. Once eligible, both must bind exact asset membership, hashes, groups, splits, rights/mapping/source policies and coverage/dedup evidence. Reproducibility requires matching semantic identities from a second clean process-level build over unchanged inputs.

## DF-G8 — model entry

`CERT-MK1-DF-CORPUS-001` is `OPEN`. `build_corpus_closure_readiness.py --require-modeling-ready` must remain non-zero and `modeling_allowed=false` until the named corpus certificate is certified with `gap_codes=[]` and all required closure evidence PASS.

No Benchmark A/B/C, model training, threshold calibration, replay progression or real-camera progression is authorized before that transition.

## Certificate lineage

```text
CERT-MK1-DF-SPEC-001        CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001..003 historical / invalidated
CERT-MK1-DF-TOOLCHAIN-004   INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005   CANDIDATE
CERT-MK1-DF-SONYC-001       CERTIFIED / scoped
EMP-DATASET-001              OPEN
EMP-DATA-QUALITY-001         OPEN
CERT-MK1-DF-CORPUS-001      OPEN
```

`TOOLCHAIN-005` may become CERTIFIED only after the active closure implementation stabilizes and fresh exact Foundry CI, free-tier and empirical cascade evidence are bound. A green unit-test run alone is not certification.

## Invalidation

Changes to taxonomy, source/acquisition semantics, rights/mapping/review, probing/fingerprints, grouping/dedup, split/coverage/freeze/handoff logic, readiness/model-entry guard, SONYC persistence, certified tests/schemas/workflows, governing documentation or `ECHO-FREE-TIER-001` require dependency review and selective recertification.
