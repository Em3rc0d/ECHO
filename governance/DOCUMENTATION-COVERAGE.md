# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-009`  
**Current Markdown corpus:** `213 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-15-SPLIT-CLOSURE-009.md`

## Rule

ECHO is documentation-first and evidence-first. Documentation preserves `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION`, and `TARGET`. Green CI does not manufacture corpus/model evidence. All truth inherits `ECHO-FREE-TIER-001`.

## Certificate lineage

```text
CERT-DOC-001..007  historical / invalidated
CERT-DOC-008       historical / 212 files / invalidated by split cascade
CERT-DOC-009       current / 213 files / CERTIFIED
```

DOC-009 adds exactly one Markdown record relative to DOC-008: `DOCUMENTATION-AUDIT-2026-09-15-SPLIT-CLOSURE-009.md`.

## Current audited truth

```text
CERT-DOC-009                    = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004       = INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005       = CANDIDATE
CERT-MK1-DF-SONYC-001           = CERTIFIED
CANONICAL_FINGERPRINTS           = PASS 1081/1081
GLOBAL_DEDUP                     = PASS
RECORDING_FAMILY_AUDIT           = PASS
SPLIT_INTEGRITY                  = PASS
COVERAGE                         = FAIL
EMP-MK1-CORPUS-READINESS-001    = BLOCKED
CERT-MK1-DF-CORPUS-001          = OPEN
modeling_allowed                 = false
Benchmark A/B/C                  = LOCKED
ECHO-FREE-TIER-001               = PASS
```

Authoritative readiness is `MK1/mining-site/materialization/corpus-closure-readiness.json` at `589e7f4affed39e1ffcf6f50602d79587560bbb3`, evidence identity `c20eab44bae7cb10e7038833fdf46741d9d4c1574ebfe1b65e47dd6db160249b`.

Split integrity now passes via deterministic whole-group quarantine: three conflicting acoustic groups / 62 assets remain evidence but do not enter development coverage or frozen membership. The current development set has 1016 assets.

Three ledger rights/semantic rows remain fail-closed. Coverage remains the empirical bottleneck: FIRE_ALARM/TIRE_SQUEAL positives, GLASS_SHATTER source concentration, background source diversity and per-target hard-negative source/asset deficits.

## Automated governance

`scripts/check_documentation_governance.py` enforces:

- immutable promise and free-tier ancestor;
- DOC-009 current / DOC-008 invalidated;
- SONYC-001 certified and TOOLCHAIN-005 still candidate;
- exact ledger/readiness identities;
- dedup/family/split PASS;
- exactly 3 quarantined groups / 62 quarantined assets / 1016 eligible assets;
- exact 19 readiness gaps;
- corpus certificate OPEN and `modeling_allowed=false`;
- 213 Markdown files and no merge-conflict markers.

## Invalidation

DOC-009 becomes stale if the 213-file inventory, durable ledger/closure/readiness evidence, certificate/policy truth, rights/semantics/grouping/split/coverage/freeze logic, immutable promise, or `ECHO-FREE-TIER-001` changes without a fresh audit.
