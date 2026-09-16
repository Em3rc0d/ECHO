# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-010`  
**Current Markdown corpus:** `214 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-15-CORPUS-CLOSURE-010.md`

## Rule

ECHO is documentation-first and evidence-first. Documentation preserves the distinction `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION`, and `TARGET`. Green CI never manufactures empirical corpus/model evidence. All current truth inherits `ECHO-FREE-TIER-001`.

## Certificate lineage

```text
CERT-DOC-001..009  historical / invalidated
CERT-DOC-010       current / 214 files / CERTIFIED
```

DOC-010 adds exactly one Markdown record relative to the 213-file DOC-009 corpus and re-audits the durable post-Till corpus evidence.

## Current audited truth

```text
CERT-DOC-010                    = CERTIFIED
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

The authoritative durable readiness artifact is `MK1/mining-site/materialization/corpus-closure-readiness.json` at `main@60dfa361eb344172973a96949d38e137fbfaf822`, evidence identity `7c3dd6d518d8bc088a419b39e4dfb4894482def44906ca4561a4cc84f631f389`.

Canonical ledger truth is 1159 corpus-facing rows with 1159/1159 canonical fingerprints and zero unresolved corpus-facing blockers. The summary baseline is `05433347ebc35e67ab9f3bbd78a9e3a64c0bb9aa`, ledger identity `d4c0e78ef9111ef2cf3f2a44a9aea9d1e009afb5424dc7c851cbc9883186d19a`. Dedup, recording-family and split-integrity are PASS.

Final coverage remains FAIL with exactly 17 detailed gaps. They reduce to FIRE positive/group/split coverage, TIRE positive/group/split coverage and GLASS source concentration. Background and governed hard-negative floors remain closed.

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

## Candidate acquisition boundary

PR #33 changes Public Gap acquisition/persistence and proposes additional exact Wikimedia FIRE candidates. That branch-level intent is documented, but candidate rows receive zero durable corpus credit until `main` materializes real bytes and the canonical ledger → grouping/dedup → split → coverage cascade is recomputed.

Consequently DOC-010 freezes the existing durable counts, not predicted post-merge counts.

## Automated governance

`scripts/check_documentation_governance.py` validates:

- immutable promise and `ECHO-FREE-TIER-001`;
- DOC-010 current / DOC-001..009 invalidated;
- SONYC-001 scoped certification;
- TOOLCHAIN-004 invalidated / TOOLCHAIN-005 candidate;
- exact audited ledger and readiness identities;
- 1159/1159 canonical fingerprints and zero ledger blockers;
- global dedup, recording-family and split-integrity PASS;
- exactly 17 detailed coverage gaps and nine readiness blockers;
- GLASS final 239 assets / 222 groups / four positive source families / 0.945607 largest-source fraction;
- TIRE hard-negative closure 25 assets / 12 groups / two source families;
- corpus certificate OPEN and `modeling_allowed=false`;
- 214-file Markdown inventory and absence of merge-conflict markers.

## Invalidation

DOC-010 becomes stale if the 214-file inventory, machine-readable ledger/closure/readiness evidence, certificate/policy truth, rights/semantics/grouping/split/coverage/freeze logic, immutable promise, product critical path or free-tier boundary changes without a fresh audit.
