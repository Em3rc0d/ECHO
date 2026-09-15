# MK1 Data Foundry — Gates and Closure Criteria

**Status:** `TOOLCHAIN_CERTIFIED / SONYC_CERTIFIED / REAL_CORPUS_CLOSURE_ACTIVE`  
**Current toolchain certificate:** `CERT-MK1-DF-TOOLCHAIN-004`  
**Current SONYC certificate:** `CERT-MK1-DF-SONYC-001`  
**Current corpus readiness:** `EMP-MK1-CORPUS-READINESS-001 = BLOCKED`  
**Global invariant:** `ECHO-FREE-TIER-001`

## Gate chain

```text
DF-G0 source registry
  -> DF-G1 release/provenance
  -> DF-G2 rights
  -> DF-G3 semantics/review
  -> DF-G4 real-byte integrity/quality + canonical fingerprint
  -> DF-G5 exact + near-duplicate / recording-family audit
  -> DF-G6 group-aware split / holdout audit
  -> coverage/diversity/hard-negative solidity
  -> DF-G7 frozen bundle
  -> second clean freeze / reproducibility
  -> CERT-MK1-DF-CORPUS-001
  -> DF-G8 model-entry gate
```

A downstream gate cannot compensate for an upstream failure. All execution inherits `ECHO-FREE-TIER-001`; paid fallbacks and lowered quality floors are forbidden.

## SONYC certified materialization node

`CERT-MK1-DF-SONYC-001` certifies SONYC-UST-V2.3 full real-media materialization:

```text
implementation baseline  ab8c47ba6aabb25390644954a2a06945ca7a81bb
SONYC run                 34922010537
verified shards           19 / 19 PASS
merge                     PASS
fingerprint contract      PASS
probe failures            0
fingerprint failures      0
durable evidence          78fc019839f1c9dad1a58a70d439605d887361d7
```

The source release contains 18,510 assets / 185,100 seconds. Durable extraction produced 236 target-candidate rows, 428 confuser-candidate rows and 599 unique fingerprinted ledger-relevant acoustic assets. Materialization review flags are never equivalent to corpus admission.

## DF-G0 — Source identity

Every selected source requires stable source/release identity, evidence URL, license model and intended role. Dataset wrappers do not automatically create independent acoustic-source credit.

## DF-G1 — Provenance/acquisition

Real coverage requires observed media bytes or a bounded source-specific materialization path. Metadata-only rows may remain evidence but do not create release-safe positive/hard-negative credit. Local asset identity uses SHA-256.

## DF-G2 — Rights

Every admitted `release_safe` asset needs a compatible rights decision. `UNKNOWN`, `REVIEW_REQUIRED`, incompatible or unresolved rights fail closed.

## DF-G3 — Semantics

Positive admission requires exact/narrow evidence or explicit asset review. Stop-lines remain:

```text
Alarm      != FIRE_ALARM
Squeak     != TIRE_SQUEAL
Car        != VEHICLE_HORN
Glassware  != GLASS_SHATTER
```

Hard negatives never become positives by convenience.

## DF-G4 — Technical evidence and fingerprints

Every admitted row requires real bytes, byte size, SHA-256, valid audio probe, positive duration, provenance and canonical fingerprint where required.

Current canonical ledger summary:

```text
entry_count                         1164
canonical_fingerprint_count         1164
canonical_fingerprint_missing_count    0
exact_duplicate_sha256_group_count     0
status = PASS_CONSOLIDATED_WITH_OPEN_GATES
```

Canonical fingerprint coverage is complete. Ledger admission is not: current blocking-reason counts include `GROUPING_GLOBAL_AUDIT_REQUIRED=503`, `NO_EXACT_SEMANTIC_ROLE=83`, `AUGMENTATION_ONLY_NO_REAL_SOURCE_CREDIT=4`, plus one license conflict, one rights-text conflict and two target semantic-status conflicts.

## DF-G5 — Global duplicate / recording-family audit

The refreshed closure evidence currently says:

```text
global-dedup-audit.json       = FAIL
recording-family-audit.json    = FAIL
```

Final certification requires canonical transcode-aware near-duplicate handling and global recording-family/source-independence review, with no protected-split leakage.

## DF-G6 — Split integrity

Current `split-integrity.json = FAIL`.

Group-aware splitting must ultimately prove:

```text
group overlap = 0
exact duplicate overlap = 0
near-duplicate overlap = 0
field holdout overlap = 0
```

Seed shopping/manual clip movement to manufacture coverage is forbidden.

## Corpus solidity

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

Global negatives: >=200 assets / >=50 groups / >=3 sources. Per-target hard negatives: >=20 assets / >=10 groups / >=2 sources.

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

Current coverage gate is `FAIL`; no floor may be lowered to obtain certification.

## Exact current readiness blockers

`EMP-MK1-CORPUS-READINESS-001` at `de1d31b280e9fad4a3764537aa75d7d72802adb7` is `BLOCKED`, `eligible_for_certificate_review=false`, `modeling_allowed=false`.

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
LEDGER_AUGMENTATION_ONLY_NO_REAL_SOURCE_CREDIT_4
LEDGER_GROUPING_GLOBAL_AUDIT_REQUIRED_503
LEDGER_LICENSE_NOT_RELEASE_SAFE_1
LEDGER_NO_EXACT_SEMANTIC_ROLE_83
LEDGER_RIGHTS_TEXT_CONFLICT_REVIEW_REQUIRED_1
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

## DF-G7 — Freeze and reproducibility

Current evidence is fail-closed:

```text
corpus-freeze-1.validation.json = FAIL
corpus-freeze-2.validation.json = FAIL
corpus-reproducibility.json     = FAIL
```

Freeze #1 must bind exact asset membership, hashes, recording families, splits, rights/mapping/source policies, coverage and dedup/quarantine evidence. A second clean freeze over unchanged inputs must reproduce semantic identity.

## DF-G8 — Model-entry handoff

`CERT-MK1-DF-CORPUS-001` remains `OPEN`. The reusable MK1 Model Entry Gate runs `build_corpus_closure_readiness.py --require-modeling-ready` and fails until the named corpus certificate is `CERTIFIED`, all required closure evidence passes and `gap_codes=[]`. Future model/benchmark/train workflows are checked for bypass wiring.

## Certificate lineage

```text
CERT-MK1-DF-SPEC-001       CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001  historical
CERT-MK1-DF-TOOLCHAIN-002  historical
CERT-MK1-DF-TOOLCHAIN-003  INVALIDATED / historical
CERT-MK1-DF-TOOLCHAIN-004  CERTIFIED / current
CERT-MK1-DF-SONYC-001      CERTIFIED / scoped current
EMP-DATASET-001             OPEN
EMP-DATA-QUALITY-001        OPEN
CERT-MK1-DF-CORPUS-001     OPEN
```

Toolchain-004 is tied to implementation baseline `ab8c47ba6aabb25390644954a2a06945ca7a81bb`, Data Foundry CI `34922010529`, Free-Tier `34922010518` and real SONYC run `34922010537`.

## Invalidation

Changes to taxonomy, source/acquisition semantics, rights/mapping/review, probing/fingerprints, SONYC persistence, grouping/dedup, split/coverage/freeze/handoff logic, readiness/model-entry guard, certified tests/schemas/workflows or `ECHO-FREE-TIER-001` invalidate dependent evidence until rerun/review.
