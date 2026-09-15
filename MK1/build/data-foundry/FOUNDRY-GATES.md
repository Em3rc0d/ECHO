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

A downstream gate cannot compensate for an upstream failure. Paid fallbacks and lowered quality floors are forbidden.

## SONYC materialization node

`CERT-MK1-DF-SONYC-001` is now `CERTIFIED` for SONYC-UST-V2.3 full real-media materialization. Exact evidence:

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

The source release contains 18,510 assets / 185,100 seconds. The durable ledger-relevant extraction produced 236 target-candidate rows, 428 confuser-candidate rows and 599 unique fingerprinted ledger-relevant acoustic assets. Review flags in the materialization summary are not silently converted into corpus admission.

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

After SONYC integration the canonical ledger reports:

```text
ledger entries        1164
fingerprints present  1164
fingerprints missing     0
```

The previous canonical-fingerprint coverage gap is closed. This does not close semantic/source/coverage gaps.

## DF-G5 — Global duplicate / recording-family audit

Final corpus certification still requires PASS evidence for global exact + cross-format near-duplicate handling and recording-family/source-independence grouping. Protected-split leakage is forbidden.

Required outputs include `global-dedup-audit.json` and `recording-family-audit.json` with closure-compatible PASS semantics.

## DF-G6 — Split integrity

Group-aware splitting must preserve:

```text
group overlap = 0
exact duplicate overlap = 0
near-duplicate overlap = 0
field holdout overlap = 0
```

Seed shopping or manual clip movement to manufacture coverage is forbidden. Required output: `split-integrity.json = PASS`.

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

Current positive assets:

```text
FIRE_ALARM       5 / 50
GLASS_SHATTER  286 / 50
SIREN          242 / 50
TIRE_SQUEAL      5 / 50
VEHICLE_HORN   326 / 50
```

Current hard-negative assets / source families:

```text
FIRE_ALARM      34 / 1
GLASS_SHATTER  401 / 1
SIREN          365 / 4
TIRE_SQUEAL      0 / 0
VEHICLE_HORN    33 / 1
```

Current readiness gap codes:

```text
FIRE_ALARM_ASSETS_5_LT_50
TIRE_SQUEAL_ASSETS_5_LT_50
TIRE_SQUEAL_UNDERLYING_SOURCES_1_LT_2
FIRE_ALARM_HARD_NEGATIVE_SOURCES_1_LT_2
GLASS_SHATTER_HARD_NEGATIVE_SOURCES_1_LT_2
VEHICLE_HORN_HARD_NEGATIVE_SOURCES_1_LT_2
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVE_GROUPS_0_LT_10
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2
```

No floor may be lowered to obtain certification. Required coverage output remains `coverage-gate.json` with `status=PASS` and `gap_codes=[]` before corpus certification.

## DF-G7 — Freeze and reproducibility

Freeze #1 must bind exact asset membership, hashes, recording families, splits, rights/mapping/source policies, coverage and dedup/quarantine evidence. A second clean freeze over unchanged inputs must reproduce semantic identity.

Required outputs:

```text
corpus-freeze-1.validation.json = PASS
corpus-freeze-2.validation.json = PASS
corpus-reproducibility.json = PASS
```

## Readiness and certificate review

Current authoritative readiness:

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
```

`CERT-MK1-DF-SONYC-001` does not alter this predicate. It closes one scoped upstream materialization claim only.

## DF-G8 — Model-entry handoff

The reusable MK1 Model Entry Gate runs `build_corpus_closure_readiness.py --require-modeling-ready` and fails until the named corpus certificate is `CERTIFIED`, all required closure evidence passes and no gap remains. Future model/benchmark/train workflows are checked for bypass wiring.

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
