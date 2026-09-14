# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-005`  
**Current Markdown corpus:** `208 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-14-CORPUS-READINESS.md`

## Rule

ECHO is documentation-first and evidence-first. Any substantive `KNOWLEDGE`, `DECISION`, `PLAN`, `BUILD_SPEC`, `TEST_SPEC` or `LEDGER` artifact must be reconstructible without consulting the original chat. Applicable content includes purpose/scope, upstream dependencies, definitions, evidence, alternatives/trade-offs, current decision, rationale, risks, validation, downstream consumers, open nodes, invalidation and provenance.

Compact README/index/schema files may be short when their role is narrow. A small file is not acceptable when it hides an undeveloped substantive decision.

## Epistemic separation

Use and preserve the distinction:

```text
FACT/EVIDENCE
INFERENCE
HYPOTHESIS
DECISION
TARGET
```

A target or planned threshold is never presented as a measured result. A green software CI does not certify real-world data/model behavior.

## Coherence checks

Documentation fails if it:

- contradicts `PROJECT-CHARTER.md` or `ECHO-FREE-TIER-001`;
- presents a historical certificate as current;
- hides an empirical gap behind a status label;
- lets prose disagree materially with machine-readable policy/evidence;
- reintroduces paid/self-hosted execution as a required path;
- allows model work before `CERT-MK1-DF-CORPUS-001`;
- claims `CERTIFIED` when required downstream evidence remains missing.

## Certificate lineage

```text
CERT-DOC-001  historical / invalidated
CERT-DOC-002  historical / invalidated
CERT-DOC-003  historical / 197 files / invalidated
CERT-DOC-004  historical / 206 files / invalidated by readiness/toolchain delta
CERT-DOC-005  current / 208 files / CERTIFIED
```

`CERT-DOC-005` adds two new substantive Markdown records relative to the 206-file corpus:

```text
MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-003.md
governance/DOCUMENTATION-AUDIT-2026-09-14-CORPUS-READINESS.md
```

All other documentation changes in the same recertification update existing files in place.

## Current audited truth

The current documentation must consistently show:

```text
CERT-DOC-005                    = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-003       = CERTIFIED
EMP-MK1-CORPUS-READINESS-001    = BLOCKED
CERT-MK1-DF-CORPUS-001          = OPEN
modeling_allowed                = false
Benchmark A/B/C                 = LOCKED
ECHO-FREE-TIER-001              = PASS / global invariant
```

The authoritative empirical readiness state is machine-readable at:

`MK1/mining-site/materialization/corpus-closure-readiness.json`.

Documentation may summarize that file but may not weaken or override its gap semantics.

## Current audit result

`CERT-DOC-005` reviewed the delta introduced by canonical-ledger consolidation, readiness/guard implementation and Data Foundry toolchain recertification 003. The audit verified that current state, certificate ledger, Foundry gates and automated governance all preserve the fail-closed release law.

The current audit does **not** certify final admitted corpus counts/groups/duration, duplicate absence, model quality, thresholds, capacity or field performance.

## Automated governance

`scripts/check_documentation_governance.py` enforces high-authority invariants including:

- immutable promise presence;
- current documentation/toolchain certificate IDs;
- current 208-file Markdown inventory;
- corpus certificate remains OPEN until empirical closure;
- readiness status/model lock visibility;
- free-tier invariant;
- absence of stale self-hosted/120 GiB required-path guidance;
- closure-critical markers and unresolved merge conflicts.

Automated checks complement, not replace, substantive human/agent review.

## Invalidation

`CERT-DOC-005` becomes stale if:

- the Markdown inventory changes from 208 without audit;
- substantive Markdown/policy truth changes without dependency review;
- an authoritative document becomes a stub or contradiction;
- toolchain/corpus/model certificate state changes without synchronization;
- machine-readable readiness and prose disagree materially;
- the promise or free-tier boundary changes.

The documentation gate remains PASS only while a future engineer/agent can reconstruct current scope, evidence, decisions, blockers and authorized next transition from the repository itself.
