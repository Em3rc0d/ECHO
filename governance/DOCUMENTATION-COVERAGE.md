# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-011`  
**Current Markdown corpus:** `215 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-15-CORPUS-CLOSURE-011.md`

## Rule

ECHO is documentation-first and evidence-first. Documentation preserves `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION`, and `TARGET`. Green CI never manufactures empirical corpus/model evidence. All current truth inherits `ECHO-FREE-TIER-001`.

## Certificate lineage

```text
CERT-DOC-001..010  historical / invalidated
CERT-DOC-011       current / 215 files / CERTIFIED
```

## Current audited truth

```text
CERT-DOC-011                    = CERTIFIED
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

The authoritative durable readiness artifact is at `main@2088c93d65b5d4dff58bb5cdb91b0e76e6288afb`, evidence identity `9b6da43da378dbf546a3961c6ed47b8e7218b5135bbe84680f58eecf86030559`.

Canonical ledger truth is 1162 corpus-facing rows with 1162/1162 canonical fingerprints, zero blockers, baseline `0e05b9ce7ef9afdbd6d0d327922f9811fa0a50d7`, ledger identity `b250b18e8ccef3776cdc38d42f240a057bcf99b260cc6cb58a77aad93e9d0cab`. Dedup, recording-family and split-integrity are PASS.

Final coverage remains FAIL with exactly 17 detailed gaps. FIRE improved durably to 12 assets / 9 groups / 3 source families / 311.05767 s, with train 10/7 groups, validation 2/2 and test 0/0. TIRE remains 11/11; GLASS remains 239/222 with 0.945607 largest-source fraction.

## Product-direction audit

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

## Freesound orchestration boundary

The next authorized acquisition is exact, release-safe FIRE/TIRE audio. Generated Freesound evidence is bound to the triggering SHA and must fail closed when `main` moves. Workflow YAML edits do not self-trigger materialization. Raw supplemental semantic-config pushes trigger the release-safe Freesound materializer, not Canonical Ledger directly; the ledger waits for durable materialization evidence/successful materialization workflow. The narrower CC0 materializer does not race supplemental changes.

Future Freesound candidates receive zero corpus credit until the durable materialization → ledger → grouping/dedup → split → coverage → readiness cascade completes.

## Automated governance

`scripts/check_documentation_governance.py` validates:

- immutable promise and `ECHO-FREE-TIER-001`;
- DOC-011 current / DOC-001..010 invalidated;
- SONYC-001 scoped certification;
- TOOLCHAIN-004 invalidated / TOOLCHAIN-005 candidate;
- audited ledger/readiness identities and 1162/1162 fingerprints;
- zero ledger blockers;
- grouping, dedup and split integrity PASS;
- exactly 17 detailed coverage gaps and nine readiness blockers;
- FIRE final 12 assets / 9 groups / 3 sources;
- GLASS final 239 / 222 / 0.945607 concentration;
- TIRE HN 25 / 12 / 2 closure;
- corpus certificate OPEN and `modeling_allowed=false`;
- 215-file Markdown inventory and no merge-conflict markers.

## Invalidation

DOC-011 becomes stale if the 215-file inventory, durable ledger/coverage/readiness evidence, certificate/policy truth, rights/semantics/grouping/split/coverage/freeze logic, immutable promise, product critical path or free-tier boundary changes without a fresh audit.
