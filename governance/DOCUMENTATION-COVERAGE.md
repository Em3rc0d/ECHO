# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-012`  
**Current Markdown corpus:** `216 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-16-CORPUS-CLOSURE-012.md`

## Rule

ECHO is documentation-first and evidence-first. Documentation preserves `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION`, and `TARGET`. Green CI never manufactures empirical corpus/model evidence. All current truth inherits `ECHO-FREE-TIER-001`.

## Certificate lineage

```text
CERT-DOC-001..011  historical / invalidated
CERT-DOC-012       current / 216 files / CERTIFIED
```

## Current audited truth

```text
CERT-DOC-012                    = CERTIFIED
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

The authoritative durable readiness artifact is at `main@48af9f220b30f2197aa376bff025195cb0a2a13b`, evidence identity `85dee5596dbc9c88e0430e32b5e8eec7c014d526d132974542b2e4a36a108a50`.

Canonical ledger truth is 1141 corpus-facing rows with 1141/1141 canonical fingerprints, zero blockers, baseline `050f2ebc39fea0d1e6903190ad471fd97d1487dc`, ledger identity `1ab3712452f42205fe9004f1d6cb9e778297487891bb373e5c42d635854f1d85`. Dedup, recording-family and split-integrity are PASS.

Final coverage remains FAIL with exactly 16 detailed gaps. FIRE is 19 assets / 16 groups / 3 source families / 460.864037 s. TIRE is 14 assets / 10 groups / 2 source families / 344.600098 s. GLASS is 222 assets / 205 groups with 0.941441 largest-source fraction. Background and all required hard-negative floors remain closed.

## External-evidence drift

The live release-safe Freesound rebuild reduced several Freesound-backed counts relative to DOC-011. ECHO deliberately accepted the current materializable/rights evidence and rebuilt the full closure chain instead of retaining stale credit. This is a fail-closed behavior and does not authorize floor relaxation or hidden restoration of unavailable rows.

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

## Acquisition boundary

New source lanes may materialize public rights/provenance/bytes/probe/fingerprint evidence before admission, but they receive zero corpus, split, coverage or diversity credit until source identity is reviewed, canonical ledger integration is explicit, and the complete grouping/dedup/split/coverage/readiness cascade succeeds.

Freesound evidence remains bound to the triggering SHA and must fail closed when `main` moves. Wrapper datasets/hosting sites do not create independent acoustic source families.

## Automated governance

`scripts/check_documentation_governance.py` validates:

- immutable promise and `ECHO-FREE-TIER-001`;
- DOC-012 current / DOC-001..011 invalidated;
- SONYC-001 scoped certification;
- TOOLCHAIN-004 invalidated / TOOLCHAIN-005 candidate;
- exact ledger/readiness identities and 1141/1141 fingerprints;
- zero ledger blockers;
- grouping, dedup and split-integrity PASS;
- exactly 16 detailed coverage gaps and nine readiness blockers;
- FIRE final 19 assets / 16 groups / 3 sources / exact split truth;
- GLASS final 222 / 205 / 0.941441 concentration;
- TIRE final 14 / 10 plus HN 25 / 12 / 2 closure;
- final asset-quality stop lines all zero;
- corpus certificate OPEN and `modeling_allowed=false`;
- 216-file Markdown inventory and absence of merge-conflict markers.

## Invalidation

DOC-012 becomes stale if the 216-file inventory, durable ledger/coverage/readiness evidence, certificate/policy truth, rights/semantics/grouping/split/coverage/freeze logic, immutable promise, product critical path or free-tier boundary changes without a fresh audit.
