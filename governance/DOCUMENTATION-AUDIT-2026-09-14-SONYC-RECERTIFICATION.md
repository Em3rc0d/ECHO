# Documentation Audit — SONYC Recertification / 2026-09-14

**Certificate:** `CERT-DOC-006`  
**Status:** `CERTIFIED`  
**Scope:** documentation delta caused by SONYC v2.3 full real-media materialization, Data Foundry toolchain recertification 004, and refreshed corpus evidence.  
**Global invariant:** `ECHO-FREE-TIER-001`

## 1. Reason for re-audit

`CERT-DOC-005` certified the prior 208-file Markdown corpus and the `CERT-MK1-DF-TOOLCHAIN-003` baseline. The SONYC fingerprint validator, durable-persistence workflow and tests changed materially, and a real 19-shard SONYC materialization was subsequently persisted and integrated into the canonical corpus ledger. Keeping DOC-005 or TOOLCHAIN-003 labelled as current would therefore be documentation drift.

## 2. Exact evidence reviewed

This audit binds the following concrete evidence:

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

`CERT-MK1-DF-SONYC-001` is backed by 19/19 successful shards, merge PASS, canonical fingerprint contract PASS, zero probe failures, zero fingerprint failures and durable evidence persistence.

## 3. Current empirical truth

The refreshed readiness artifact is authoritative and remains fail-closed:

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
```

The canonical ledger now reports complete canonical fingerprint coverage:

```text
ledger entries        1164
fingerprints present  1164
fingerprints missing     0
```

Current positive assets before final corpus certification:

```text
FIRE_ALARM       5
GLASS_SHATTER  286
SIREN          242
TIRE_SQUEAL      5
VEHICLE_HORN   326
```

Current hard-negative assets / source families:

```text
FIRE_ALARM      34 / 1
GLASS_SHATTER  401 / 1
SIREN          365 / 4
TIRE_SQUEAL      0 / 0
VEHICLE_HORN    33 / 1
```

Current readiness gap codes are:

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

The historical `CANONICAL_FINGERPRINT_COVERAGE_INCOMPLETE`, SIREN hard-negative-source deficit, and VEHICLE_HORN zero-hard-negative count are no longer current claims and must not remain in current-state documentation.

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

SONYC certification is intentionally narrower than corpus certification. It proves the SONYC v2.3 materialization/fingerprint/persistence claim and does not manufacture downstream coverage, grouping, split, freeze or reproducibility evidence.

## 5. Markdown corpus accounting

`CERT-DOC-005` covered 208 Markdown files. This certification delta adds exactly two substantive Markdown records:

```text
+ MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-004.md
+ governance/DOCUMENTATION-AUDIT-2026-09-14-SONYC-RECERTIFICATION.md
```

The SONYC materialization certificate is machine-readable JSON, and all other documentation changes update existing files in place. The resulting documentation corpus is therefore **210 Markdown files**.

## 6. Release law preserved

No certification in this delta unlocks model work. The executable rule remains:

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

The certified SONYC path used standard GitHub-hosted execution, bounded sharding, one-day evidence artifacts, local Python/FFmpeg tooling and compact durable evidence. No paid runner, GPU, model API, dataset purchase, storage tier or overage route is required. `ECHO-FREE-TIER-001` remains PASS and universal.

## 8. Epistemic separation

- **FACT/EVIDENCE:** exact workflow outcomes, hashes/commits, SONYC summary counts/digests, current ledger/readiness counts and gap codes.
- **DECISION:** SONYC materialization and current toolchain are certified; corpus/model remain gated.
- **TARGET:** future `gap_codes=[]`, two clean freezes and reproducible corpus identity.
- **OPEN EMPIRICAL CLAIM:** final admitted corpus identity, complete corpus quality closure, model metrics, thresholds and field behavior.

## 9. Result

The documentation delta is coherent and reconstructible after synchronizing Current State, Documentation Coverage, Certification Ledger, Foundry Gates and automated documentation governance.

```text
CERT-DOC-006 = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004 = CERTIFIED
CERT-MK1-DF-SONYC-001 = CERTIFIED
CERT-MK1-DF-CORPUS-001 = OPEN
modeling_allowed = false
```

## 10. Invalidation

`CERT-DOC-006` becomes stale if the 210-file Markdown inventory changes without audit, substantive certification/policy truth changes without synchronization, current prose diverges from machine-readable readiness/certificates, a governing certificate is invalidated without documentation review, or the immutable promise/free-tier boundary changes.
