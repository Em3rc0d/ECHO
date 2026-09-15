# Documentation Audit — Corpus Closure Iteration 007 / 2026-09-14

**Certificate:** `CERT-DOC-007`  
**Status:** `CERTIFIED`  
**Scope:** corpus-role boundary delta and refreshed closure/readiness evidence before global recording-group resolution.  
**Global invariant:** `ECHO-FREE-TIER-001`

## Why DOC-006 is stale

`CERT-DOC-006` certified the 210-file SONYC/toolchain-004 documentation baseline. PR #10 introduced a material Foundry semantic change: review-only materializations are no longer admitted to the corpus-facing canonical ledger. The deterministic cascade then regenerated ledger, closure and readiness evidence. Therefore both the prior toolchain certificate and prior documentation certificate are no longer current.

## Exact current evidence

```text
role-boundary implementation merge  b2fc09b1c98c4c8adcb2fe9dc4db7e1dadc61107
canonical ledger evidence            3ba3f3141a24013abf8f3cbf68f46043a149ae12
closure audits                       4ebbe3f042181ec789d26d1ff4d6ede4ba656ef9
closure readiness                    ed069c64d8b5efc855157531a6a59aadff363f40
PR #10 Data Foundry CI               34926638198 PASS / 3.10, 3.11, 3.12
PR #10 Documentation Governance      34926638112 PASS
PR #10 Free-Tier Boundary            34926638114 PASS
```

## Current ledger truth

```text
entry_count                         1081
canonical_fingerprint_count         1081
canonical_fingerprint_missing_count    0
role-boundary input rows            1164
review-only rows removed              83
GROUPING_GLOBAL_AUDIT_REQUIRED       448
```

The removed 83 rows remain in source materialization/review evidence. No labels, source families, coverage floors or acoustic content were fabricated or deleted.

The following historical ledger blockers disappeared because those rows are not corpus roles:

```text
AUGMENTATION_ONLY_NO_REAL_SOURCE_CREDIT
NO_EXACT_SEMANTIC_ROLE
RIGHTS_TEXT_CONFLICT_REVIEW_REQUIRED
```

## Current readiness truth

`EMP-MK1-CORPUS-READINESS-001` remains fail-closed:

```text
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = 6582baef9435283c4e70c25b04c211fb3cf107e752782dfbb9066b897fefff0e
```

Exact gap-code set:

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

## Certification lineage

```text
CERT-MK1-DF-SONYC-001     = CERTIFIED / unchanged scoped evidence
CERT-MK1-DF-TOOLCHAIN-004 = INVALIDATED / material Foundry semantics changed
CERT-MK1-DF-TOOLCHAIN-005 = CANDIDATE / requires final fresh closure implementation baseline + CI/free-tier evidence
CERT-DOC-006              = INVALIDATED / superseded by this audit
CERT-DOC-007              = CERTIFIED
CERT-MK1-DF-CORPUS-001    = OPEN
```

`TOOLCHAIN-005` is not certified by this audit. It can only be promoted after the active corpus-closure code stabilizes and exact CI/free-tier/empirical cascade evidence is bound.

## Global recording-group change under review

PR #11 adds conservative leakage protection. Existing source/curated groups remain edges; exact identity and governed near-duplicate fingerprint relations are unioned into deterministic global split-protection components. The change never merges or deletes content. Fallback source groups without detected acoustic relation become explicitly screened source groups rather than silently claiming curated family provenance. Any resulting original-split conflict remains a fail-closed split blocker.

## Markdown accounting

DOC-006 covered 210 Markdown files. This audit adds one Markdown record, producing **211 Markdown files** on this branch.

## Result

```text
CERT-DOC-007 = CERTIFIED
TOOLCHAIN-004 = INVALIDATED
TOOLCHAIN-005 = CANDIDATE
CORPUS-001 = OPEN
modeling_allowed = false
```

## Invalidation

DOC-007 becomes stale if the Markdown inventory, current machine-readable readiness, corpus-role/grouping semantics, certification lineage, immutable promise or `ECHO-FREE-TIER-001` changes without a new audit.
