# ECHO — Free-Tier Execution Boundary

**Status:** `FROZEN_POLICY`  
**Effective date:** 2026-09-13  
**Scope:** MK1/MK2 engineering, dataset materialization, CI, benchmark and release evidence.

## Non-negotiable rule

ECHO must not require paid infrastructure, paid API usage, larger GitHub runners, paid storage, paid GPUs, paid dataset access, or any workflow that can silently spill into billable usage.

The execution policy is deliberately stricter than provider free-tier ceilings. If a task cannot be completed inside the free boundary, ECHO must change the execution strategy, reduce working-set size, shard the workload, use a freely redistributable/public per-asset source, or leave the node explicitly open. The project must never solve a capacity problem by enabling billing.

## GitHub Actions boundary

ECHO is a public repository. Standard GitHub-hosted runners are the only hosted runners authorized by default.

Allowed runner labels:

```text
ubuntu-latest
ubuntu-24.04
ubuntu-22.04
ubuntu-slim
```

Disallowed unless this policy is explicitly replaced:

```text
larger runners
GPU runners
paid marketplace compute
private-repository minute overages
external paid CI
```

Current standard public Linux runners provide a 14 GB ephemeral SSD working volume. ECHO therefore defines a lower engineering scratch ceiling of **10 GiB per job** to preserve operating-system/tooling headroom.

## Storage budget

ECHO must not use GitHub Actions Artifacts as a dataset lake.

Hard project budgets:

- retained GitHub artifact bytes across active ECHO runs: **<= 250 MB**;
- preferred maximum artifact produced by one workflow run: **<= 100 MB**;
- artifact retention: **1 day by default**;
- large public datasets: never persisted as GitHub artifacts;
- dataset bytes: process-and-delete inside the runner whenever possible;
- Git commits contain manifests, hashes, reports, source evidence and small fixtures only, not full corpora.

These project budgets intentionally remain below the lowest GitHub Free artifact-storage allowance currently documented, leaving safety margin for unrelated artifacts and accounting delay.

GitHub cache is disabled by default for dataset bytes. If a future workflow needs cache, it requires a separate budgeted decision and cannot be used as persistent corpus storage.

## Dataset execution model

The canonical free execution sequence is:

```text
select one bounded shard / public asset batch
        ↓
download
        ↓
verify publisher/source evidence
        ↓
probe + hash + semantic/license admission
        ↓
emit small manifest/report/checkpoint
        ↓
delete raw/extracted shard
        ↓
next shard
```

A source is not allowed to force the working set above 10 GiB. Multipart archives that require more than the runner boundary simultaneously are not executed monolithically.

### Source policy under this boundary

- `SONYC-UST`: execute shard-by-shard; no full 13.3 GB residency.
- `SINGA:PURA`: execute only with a bounded extraction plan that keeps scratch <= 10 GiB.
- `FSD50K`: full multipart archive materialization is not a required release-safe dependency under standard hosted runners. Metadata and defensible per-asset subsets may be used; full-corpus execution remains optional only if a future zero-cost execution method satisfies this boundary.
- `ESC-50`: research-only; execute only when the pinned free snapshot fits the boundary.
- `UrbanSound8K`: research-only and manual-provider gated; never purchase access.
- public per-asset gap pools: preferred for closing exact target gaps because they can be materialized incrementally.
- `ECHO Field Dataset`: user-controlled/authorized capture; does not require paid cloud storage and does not count toward development-source coverage.

## No hidden billing rule

Every external service introduced later must satisfy all of the following before use:

1. zero payment method is required for the intended ECHO path;
2. hard free-tier limits are known;
3. ECHO's own budget is below those limits;
4. no auto-upgrade/overage path is required;
5. a stop-line exists before provider billing can occur;
6. the service is replaceable without changing ECHO's domain contracts.

If any item fails, the service is `DENY_FOR_ECHO_DEFAULT`.

## Certification impact

`CERT-MK1-DF-CORPUS-001` may only certify a corpus whose evidence was produced within this free-tier boundary unless a future governance decision explicitly supersedes this document.

A zero-gap requirement does **not** authorize paid infrastructure. If coverage cannot be closed for free, the correct state is:

```text
CERT-MK1-DF-CORPUS-001 = OPEN
reason = FREE_TIER_CAPACITY_OR_SOURCE_GATE
```

not a paid workaround and not fabricated evidence.

## Invalidation

This policy must be re-audited if:

- the repository becomes private;
- GitHub changes standard-runner or free-storage limits materially;
- a workflow introduces a new provider;
- artifact retention/budgets change;
- a dataset acquisition path starts requiring payment;
- a new model requires paid compute to reproduce.
