# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-008`  
**Current Markdown corpus:** `212 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-15-GROUPING-CLOSURE-008.md`

## Rule

ECHO is documentation-first and evidence-first. Documentation preserves the distinction `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION`, and `TARGET`. Green CI never manufactures empirical corpus/model evidence. All current truth inherits `ECHO-FREE-TIER-001`.

## Certificate lineage

```text
CERT-DOC-001..006  historical / invalidated
CERT-DOC-007       historical / 211 files / invalidated by grouping cascade
CERT-DOC-008       current / 212 files / CERTIFIED
```

DOC-008 adds exactly one Markdown record relative to DOC-007: `DOCUMENTATION-AUDIT-2026-09-15-GROUPING-CLOSURE-008.md`.

## Current audited truth

```text
CERT-DOC-008                    = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004       = INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005       = CANDIDATE
CERT-MK1-DF-SONYC-001           = CERTIFIED
GLOBAL_DEDUP                     = PASS
RECORDING_FAMILY_AUDIT           = PASS
SPLIT_INTEGRITY                  = FAIL
EMP-MK1-CORPUS-READINESS-001    = BLOCKED
CERT-MK1-DF-CORPUS-001          = OPEN
modeling_allowed                 = false
Benchmark A/B/C                  = LOCKED
ECHO-FREE-TIER-001               = PASS
```

The authoritative readiness artifact is `MK1/mining-site/materialization/corpus-closure-readiness.json` at `8e7702a2bf629642f78859763dabbe09df03df02`, evidence identity `fcd07c11d3291d5a78ee28cae93e42de0f16e78522720e78fffb5e71b4bcf129`.

Canonical ledger truth is 1081 corpus-facing rows with 1081/1081 canonical fingerprints. Global grouping resolved all 448 former fallback grouping blockers. Fresh dedup and recording-family audits are PASS. Three row-level rights/semantic blockers and three protected-split conflict components remain fail-closed.

## Automated governance

`scripts/check_documentation_governance.py` validates:

- immutable promise and `ECHO-FREE-TIER-001`;
- DOC-008 current / DOC-007 invalidated;
- SONYC-001 scoped certification;
- TOOLCHAIN-004 invalidated / TOOLCHAIN-005 candidate;
- exact audited ledger and readiness identities;
- global dedup and recording-family PASS;
- split FAIL with exactly three audited conflicts;
- corpus certificate OPEN and `modeling_allowed=false`;
- 212-file Markdown inventory and absence of merge-conflict markers.

## Invalidation

DOC-008 becomes stale if the 212-file inventory, machine-readable ledger/closure/readiness evidence, certificate/policy truth, rights/semantics/grouping/split/coverage/freeze logic, immutable promise, or free-tier boundary changes without a fresh audit.
