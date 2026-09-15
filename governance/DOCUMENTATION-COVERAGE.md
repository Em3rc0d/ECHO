# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-009`  
**Current Markdown corpus:** `213 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-15-CORPUS-CLOSURE-009.md`

## Rule

ECHO is documentation-first and evidence-first. Documentation preserves the distinction `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION`, and `TARGET`. Green CI never manufactures empirical corpus/model evidence. All current truth inherits `ECHO-FREE-TIER-001`.

## Certificate lineage

```text
CERT-DOC-001..007  historical / invalidated
CERT-DOC-008       historical / 212 files / invalidated by post-grouping closure changes
CERT-DOC-009       current / 213 files / CERTIFIED
```

DOC-009 adds exactly one Markdown record relative to the 212-file DOC-008 corpus: `DOCUMENTATION-AUDIT-2026-09-15-CORPUS-CLOSURE-009.md`.

## Current audited truth

```text
CERT-DOC-009                    = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004       = INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005       = CANDIDATE
CERT-MK1-DF-SONYC-001           = CERTIFIED
GLOBAL_DEDUP                     = PASS
RECORDING_FAMILY_AUDIT           = PASS
SPLIT_INTEGRITY                  = PASS
LEDGER_BLOCKERS                  = 0
EMP-MK1-CORPUS-READINESS-001    = BLOCKED
CERT-MK1-DF-CORPUS-001          = OPEN
modeling_allowed                 = false
Benchmark A/B/C                  = LOCKED
ECHO-FREE-TIER-001               = PASS
```

The authoritative readiness artifact is `MK1/mining-site/materialization/corpus-closure-readiness.json` at main commit `d94eff2958bbe57076610524cbb192d14ec95739`, evidence identity `90f2dd006cfbacfe9dc1bdc5cb81c7d9411ccf5322d6ca2dd53f334e76c209e8`.

Canonical ledger truth is 1078 corpus-facing rows with 1078/1078 canonical fingerprints and zero unresolved corpus-facing blockers. Dedup, recording-family and split-integrity are PASS. Current remaining blockers are real coverage/source-diversity deficits plus Freeze #1, Freeze #2, reproducibility and the final corpus certificate.

## Product-direction audit

The repository remains aligned with the immutable promise. The active critical path is:

```text
release-safe corpus
→ corpus certificate
→ Benchmark A/B/C
→ model winner
→ Event Engine
→ Edge Agent
→ MQTT/replay
→ real camera
```

Supporting camera/UI/transport work must not redefine or preempt the acoustic detection/classification core.

## Automated governance

`scripts/check_documentation_governance.py` validates:

- immutable promise and `ECHO-FREE-TIER-001`;
- DOC-009 current / DOC-008 invalidated;
- SONYC-001 scoped certification;
- TOOLCHAIN-004 invalidated / TOOLCHAIN-005 candidate;
- exact audited ledger and readiness identities;
- 1078/1078 canonical fingerprints and zero ledger blockers;
- global dedup, recording-family and split-integrity PASS;
- exact 16-gap current readiness set;
- corpus certificate OPEN and `modeling_allowed=false`;
- 213-file Markdown inventory and absence of merge-conflict markers.

## Invalidation

DOC-009 becomes stale if the 213-file inventory, machine-readable ledger/closure/readiness evidence, certificate/policy truth, rights/semantics/grouping/split/coverage/freeze logic, immutable promise, product critical path or free-tier boundary changes without a fresh audit.