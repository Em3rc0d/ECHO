# Documentation Coverage Audit

**Status:** `PASS_CURRENT_HEAD`  
**Current certificate:** `CERT-DOC-006`  
**Current Markdown corpus:** `210 files`  
**Latest audit:** `governance/DOCUMENTATION-AUDIT-2026-09-14-SONYC-RECERTIFICATION.md`

## Rule

ECHO is documentation-first and evidence-first. Any substantive `KNOWLEDGE`, `DECISION`, `PLAN`, `BUILD_SPEC`, `TEST_SPEC` or `LEDGER` artifact must be reconstructible without consulting the original chat. Applicable content includes purpose/scope, upstream dependencies, definitions, evidence, alternatives/trade-offs, current decision, rationale, risks, validation, downstream consumers, open nodes, invalidation and provenance.

Use and preserve the distinction `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION`, `TARGET`. A green CI does not certify an empirical corpus or model result.

## Certificate lineage

```text
CERT-DOC-001..004  historical / invalidated
CERT-DOC-005       historical / 208 files / invalidated by SONYC/toolchain delta
CERT-DOC-006       current / 210 files / CERTIFIED
```

DOC-006 adds exactly two Markdown records relative to DOC-005:

```text
MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-004.md
governance/DOCUMENTATION-AUDIT-2026-09-14-SONYC-RECERTIFICATION.md
```

The SONYC scoped certificate is JSON, so it does not change the Markdown count.

## Current audited truth

```text
CERT-DOC-006                    = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-003       = INVALIDATED / historical
CERT-MK1-DF-TOOLCHAIN-004       = CERTIFIED / current
CERT-MK1-DF-SONYC-001           = CERTIFIED / current scoped materialization
EMP-MK1-CORPUS-READINESS-001    = BLOCKED
CERT-MK1-DF-CORPUS-001          = OPEN
modeling_allowed                = false
Benchmark A/B/C                 = LOCKED
ECHO-FREE-TIER-001              = PASS / global invariant
```

The authoritative empirical readiness state is `MK1/mining-site/materialization/corpus-closure-readiness.json`. Documentation may summarize it but may not weaken its gap semantics.

## Current empirical synchronization

SONYC v2.3 real-media materialization run `34922010537` passed 19/19 shards, merge, fingerprint-contract validation and durable persistence at `78fc019839f1c9dad1a58a70d439605d887361d7`.

After integration, canonical fingerprint coverage is complete (`1164/1164`, missing `0`). The corpus nevertheless remains blocked by the current readiness gap codes, including FIRE_ALARM/TIRE_SQUEAL positive deficits, TIRE_SQUEAL hard-negative deficits, and hard-negative source-diversity deficits for FIRE_ALARM, GLASS_SHATTER and VEHICLE_HORN.

## Automated governance

`scripts/check_documentation_governance.py` enforces:

- immutable promise presence;
- current DOC-006 / TOOLCHAIN-004 / SONYC-001 identities;
- 210-file Markdown inventory;
- valid machine-readable SONYC certificate tied to run `34922010537` and evidence commit `78fc0198...`;
- corpus certificate remains OPEN while readiness is BLOCKED;
- `modeling_allowed=false`;
- free-tier invariant;
- closure-critical markers and absence of merge-conflict markers.

Automated checks complement, not replace, substantive review.

## Invalidation

`CERT-DOC-006` becomes stale if the Markdown inventory changes from 210 without audit, substantive policy/certification truth changes without dependency review, an authoritative document becomes contradictory, machine-readable readiness/certificates diverge from prose, or the immutable promise/free-tier boundary changes.
