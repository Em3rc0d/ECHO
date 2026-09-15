# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-007`  
**Current Markdown corpus:** `211 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-14-CORPUS-CLOSURE-ITERATION-007.md`

## Rule

ECHO is documentation-first and evidence-first. Documentation must preserve `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION`, and `TARGET`; green CI never manufactures empirical corpus/model evidence. All current truth inherits `ECHO-FREE-TIER-001`.

## Certificate lineage

```text
CERT-DOC-001..005  historical / invalidated
CERT-DOC-006       historical / 210 files / invalidated by corpus-role/readiness delta
CERT-DOC-007       current / 211 files / CERTIFIED
```

DOC-007 adds exactly one Markdown record: `DOCUMENTATION-AUDIT-2026-09-14-CORPUS-CLOSURE-ITERATION-007.md`.

## Current audited truth

```text
CERT-MK1-DF-TOOLCHAIN-004       = INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005       = CANDIDATE
CERT-MK1-DF-SONYC-001           = CERTIFIED
EMP-MK1-CORPUS-READINESS-001    = BLOCKED
CERT-MK1-DF-CORPUS-001          = OPEN
modeling_allowed                 = false
Benchmark A/B/C                  = LOCKED
ECHO-FREE-TIER-001               = PASS
```

The authoritative empirical readiness artifact is `MK1/mining-site/materialization/corpus-closure-readiness.json` at durable evidence commit `ed069c64d8b5efc855157531a6a59aadff363f40` for this audit.

Current canonical ledger truth after the corpus-role boundary is 1081 corpus-facing rows, 1081/1081 canonical fingerprints, missing 0, with 83 review-only source-evidence rows removed from corpus-facing admission while retained in source evidence.

## Automated governance

`scripts/check_documentation_governance.py` validates the immutable promise, DOC-007 lineage, SONYC-001 persistence, TOOLCHAIN-004 invalidation / TOOLCHAIN-005 candidate state, exact audited ledger/readiness identity, corpus OPEN/model locked state, Markdown inventory, closure markers and `ECHO-FREE-TIER-001`.

## Invalidation

DOC-007 becomes stale if the 211-file inventory, current machine-readable readiness, certification/policy truth, corpus-role/grouping semantics, immutable promise, or free-tier boundary changes without re-audit.
