# Documentation Audit — SONYC Recertification / 2026-09-14

**Certificate:** `CERT-DOC-006`  
**Status:** `CERTIFIED`  
**Scope:** documentation delta caused by SONYC v2.3 full real-media materialization, Data Foundry toolchain recertification 004, and refreshed corpus evidence.  
**Global invariant:** `ECHO-FREE-TIER-001`

## 1. Reason for re-audit

`CERT-DOC-005` certified the prior 208-file Markdown corpus and `CERT-MK1-DF-TOOLCHAIN-003`. The SONYC fingerprint validator, durable-persistence workflow and tests changed materially, and a real 19-shard SONYC materialization was persisted and integrated. DOC-005 and TOOLCHAIN-003 are therefore historical for current HEAD.

## 2. Exact evidence reviewed

```text
certified implementation baseline  ab8c47ba6aabb25390644954a2a06945ca7a81bb
Data Foundry CI                    34922010529  PASS / Python 3.10, 3.11, 3.12
Free-Tier Boundary                 34922010518  PASS
pre-delta Documentation Governance 34922010525  PASS
SONYC materialization              34922010537  PASS
SONYC durable evidence commit      78fc019839f1c9dad1a58a70d439605d887361d7
canonical ledger commit            c93ddb97902b3650921426aaf841473245c7908d
closure-audits commit              311cc2001931d4cceedb90ab5d21f06e15fdf881
closure-readiness commit           de1d31b280e9fad4a3764537aa75d7d72802adb7
```

`CERT-MK1-DF-SONYC-001` is backed by 19/19 successful shards, merge PASS, canonical fingerprint contract PASS, zero probe failures, zero fingerprint failures and durable persistence.

## 3. Current empirical truth

The refreshed readiness artifact at `de1d31b280e9fad4a3764537aa75d7d72802adb7` is authoritative:

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
```

The canonical ledger summary reports:

```text
status                    PASS_CONSOLIDATED_WITH_OPEN_GATES
ledger entries            1164
canonical fingerprints    1164
fingerprints missing         0
exact SHA-256 dup groups     0
```

Current pre-final positive assets / underlying source families:

```text
FIRE_ALARM       10 / 3
GLASS_SHATTER   304 / 2
SIREN           175 / 3
TIRE_SQUEAL      11 / 2
VEHICLE_HORN    245 / 3
```

Current hard-negative assets / underlying source families:

```text
FIRE_ALARM       34 / 1
GLASS_SHATTER   401 / 1
SIREN            32 / 1
TIRE_SQUEAL       0 / 0
VEHICLE_HORN      0 / 0
```

Current readiness gap codes are exactly:

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

This audit therefore does not treat complete fingerprint coverage as complete corpus readiness. Global dedup, recording-family, split, coverage, both freeze validations and reproducibility are currently present but FAIL, while ledger-level semantic/rights/source-credit blockers remain.

## 4. Certification truth promoted by this audit

```text
CERT-MK1-DF-TOOLCHAIN-003 = INVALIDATED / historical
CERT-MK1-DF-TOOLCHAIN-004 = CERTIFIED / current
CERT-MK1-DF-SONYC-001     = CERTIFIED / current scoped materialization certificate
CERT-DOC-005              = INVALIDATED / historical
CERT-DOC-006              = CERTIFIED / current
CERT-MK1-DF-CORPUS-001    = OPEN
modeling_allowed          = false
Benchmark A/B/C           = LOCKED
```

SONYC certification is narrower than corpus certification. It proves SONYC v2.3 materialization/fingerprint/persistence and does not manufacture downstream admission, grouping, split, coverage, freeze or reproducibility evidence.

## 5. Markdown corpus accounting

DOC-005 covered 208 Markdown files. This delta adds exactly:

```text
+ MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-004.md
+ governance/DOCUMENTATION-AUDIT-2026-09-14-SONYC-RECERTIFICATION.md
```

The SONYC certificate is JSON; all other Markdown files are updated in place. Result: **210 Markdown files**.

## 6. Release law preserved

```text
CERT-MK1-DF-CORPUS-001 = CERTIFIED
AND gap_codes=[]
AND required closure evidence = PASS
AND reproducibility = PASS
AND ECHO-FREE-TIER-001 = PASS
        ↓
model-entry gate PASS
```

Until then Benchmark A/B/C, model training, threshold calibration, replay and real-camera progression remain locked.

## 7. Free-tier compatibility

The certified SONYC path used standard GitHub-hosted execution, bounded sharding, one-day evidence artifacts, local Python/FFmpeg tooling and compact durable evidence. No paid runner, GPU, model API, dataset purchase, storage tier or overage route is required.

## 8. Epistemic separation

- **FACT/EVIDENCE:** workflow outcomes, hashes/commits, SONYC summary, ledger summary and exact readiness gap codes.
- **DECISION:** SONYC materialization and current toolchain are certified; corpus/model remain gated.
- **TARGET:** future `gap_codes=[]`, closure evidence PASS, two clean freezes and reproducible corpus identity.
- **OPEN EMPIRICAL CLAIM:** final admitted corpus identity, complete quality closure, model metrics, thresholds and field behavior.

## 9. Result

```text
CERT-DOC-006 = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004 = CERTIFIED
CERT-MK1-DF-SONYC-001 = CERTIFIED
CERT-MK1-DF-CORPUS-001 = OPEN
modeling_allowed = false
```

## 10. Invalidation

`CERT-DOC-006` becomes stale if the 210-file Markdown inventory changes without audit, substantive certification/policy truth changes without synchronization, prose diverges from machine-readable readiness/certificates, a governing certificate is invalidated without documentation review, or the immutable promise/free-tier boundary changes.
