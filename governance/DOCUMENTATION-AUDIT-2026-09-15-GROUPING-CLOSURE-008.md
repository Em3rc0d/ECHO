# ECHO Documentation Audit — Grouping Closure 008

**Certificate:** `CERT-DOC-008`  
**Status:** `CERTIFIED`  
**Audit date:** 2026-09-15  
**Audited repository state:** `8e7702a2bf629642f78859763dabbe09df03df02`  
**Markdown corpus:** `212 files`  
**Global ancestor:** `ECHO-FREE-TIER-001`

## Scope

This audit certifies documentation coherence after the real global acoustic grouping cascade. It does not certify the corpus or the current Data Foundry toolchain. `CERT-MK1-DF-TOOLCHAIN-005` remains `CANDIDATE`; `CERT-MK1-DF-CORPUS-001` remains `OPEN`; `modeling_allowed=false`.

## Exact empirical lineage

```text
PR #11 merge / implementation     8c547b70d23ce6c592ddd20d55ff37df9fa7fa03
main Data Foundry CI             34969860336 PASS
main Documentation Governance    34969860448 PASS
main Free-Tier Boundary          34969860642 PASS
canonical ledger run             34969860666 PASS
canonical ledger evidence        9fa3d2f90ddfb731d0921749c921ab2987d54307
closure evidence run             34969945975 PASS
closure evidence commit          e3e0f58dee3a1602e92f62c8a7708fa1e9fad9ea
readiness run                    34970028139 PASS
readiness evidence commit         8e7702a2bf629642f78859763dabbe09df03df02
```

The automation run being green means the evidence pipeline executed successfully. It does not imply the corpus gates themselves all passed.

## Closed nodes

Global acoustic grouping produced deterministic leakage-protection groups without merging or deleting media:

```text
ledger assets                            1081
canonical fingerprints                  1081 / 1081
fallback assets before grouping          448
fallback assets after grouping             0
global acoustic components                17
assets reassigned to components            97
screened fallback source groups           357
near-duplicate cross-group edges           831
content merge performed                  false
content deleted                          false
```

Fresh closure evidence now proves:

```text
global-dedup-audit.json       PASS
gap_codes                     []
recording-family-audit.json   PASS
pending global group audits   0
missing recording groups      0
```

Therefore the former readiness blockers `GLOBAL_DEDUP_AUDIT_NOT_PASS`, `RECORDING_FAMILY_AUDIT_NOT_PASS`, and `LEDGER_GROUPING_GLOBAL_AUDIT_REQUIRED_448` are closed by empirical evidence, not by weakening policy.

## Current split truth

The grouping audit exposed three genuine protected-split conflicts:

```text
split-integrity.json = FAIL
original_split_conflict_count = 3
eligible assets without assignment = 62
conflicting groups:
  global-acoustic:49755af077645d9cd379
  global-acoustic:683a2c690a388e66903b
  global-acoustic:b0a528766144425812e3
```

These conflicts may not be fixed by seed shopping or manual per-clip movement. The next authorized implementation must preserve complete acoustic components and fail closed; deterministic quarantine of an entire conflicting component is permitted only if explicitly encoded in the split policy and excluded from corpus membership/coverage.

## Current corpus-facing blockers

The canonical ledger has 1081 rows: 1078 `READY_FOR_GLOBAL_DEDUP`, 2 `REVIEW_REQUIRED`, 1 `BLOCKED`. Remaining ledger blockers are exactly:

```text
LICENSE_NOT_RELEASE_SAFE = 1
SEMANTIC_STATUS_CONFLICT_FIRE_ALARM = 1
SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL = 1
```

No unresolved rights or semantic conflict may receive corpus credit. Exclusion is acceptable; coercion is not.

## Current coverage truth

The coverage gate is still `FAIL`. Key measured deficits after grouping include:

```text
FIRE_ALARM       9 final-eligible assets / 6 groups
TIRE_SQUEAL     11 final-eligible assets / 11 groups
GLASS_SHATTER   source concentration = 0.976974 > 0.80
BACKGROUND      underlying source families = 1 < 3

hard-negative source families:
FIRE_ALARM       1 < 2
GLASS_SHATTER    1 < 2
SIREN            1 < 2
TIRE_SQUEAL      0 < 2 and 0 assets < 20
VEHICLE_HORN     0 < 2 and 0 assets < 20
```

Split-specific FIRE_ALARM and TIRE_SQUEAL floors also fail. These deficits require genuine independent real-media evidence; Freesound wrappers cannot be double-counted as separate acoustic source families.

## Authoritative readiness

`MK1/mining-site/materialization/corpus-closure-readiness.json` at `8e7702a2bf629642f78859763dabbe09df03df02`:

```text
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = fcd07c11d3291d5a78ee28cae93e42de0f16e78522720e78fffb5e71b4bcf129
```

Exact readiness gap set contains 20 codes:

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
LEDGER_LICENSE_NOT_RELEASE_SAFE_1
LEDGER_SEMANTIC_STATUS_CONFLICT_FIRE_ALARM_1
LEDGER_SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL_1
REPRODUCIBILITY_NOT_PASS
SIREN_HARD_NEGATIVE_SOURCES_1_LT_2
SPLIT_INTEGRITY_NOT_PASS
TIRE_SQUEAL_ASSETS_11_LT_50
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2
VEHICLE_HORN_HARD_NEGATIVES_0_LT_20
VEHICLE_HORN_HARD_NEGATIVE_SOURCES_0_LT_2
```

Readiness precheck counts and final coverage counts have different purposes. The readiness list intentionally uses pre-final ledger counts while `coverage-gate.json` applies split eligibility and all final solidity checks.

## Certification lineage

```text
CERT-DOC-006              INVALIDATED / historical
CERT-DOC-007              INVALIDATED / superseded by fresh grouping evidence
CERT-DOC-008              CERTIFIED / current
CERT-MK1-DF-TOOLCHAIN-004 INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005 CANDIDATE
CERT-MK1-DF-SONYC-001     CERTIFIED / scoped
CERT-MK1-DF-CORPUS-001    OPEN
```

## Non-claims

DOC-008 does not claim split PASS, coverage PASS, freeze/reproducibility PASS, final corpus membership, model quality, threshold calibration, replay readiness, camera readiness, or final MK1 release.

## Invalidation

`CERT-DOC-008` invalidates on any Markdown inventory change, material Foundry semantic change, new durable ledger/closure/readiness evidence, policy/source/mapping/split/coverage/freeze change, certificate-state change, or violation of `ECHO-FREE-TIER-001`. A fresh audit must bind the new exact state.
