# ECHO — Free-Tier Execution Boundary

**Status:** `FROZEN_GLOBAL_POLICY`  
**Policy ID:** `ECHO-FREE-TIER-001`  
**Effective date:** 2026-09-13  
**Scope:** **all ECHO MKs, engineering, research execution, dataset materialization, CI, benchmarks, model evaluation, integration, certification and release evidence.**

## Global non-negotiable invariant

ECHO must remain **under boundary** by default for the entire project lifecycle.

That means ECHO must not require paid infrastructure, paid API usage, larger GitHub runners, paid storage, paid GPUs, paid dataset access, or any workflow that can silently spill into billable usage.

This is not only a MK1/MK2 optimization. It is a project-level architectural invariant inherited by every later MK unless the user explicitly replaces this governance rule in a future recorded decision.

```text
0 USD required path
+ no automatic overage
+ no hidden billing fallback
+ no quality reduction to fake closure
= ECHO default execution contract
```

The execution policy is deliberately stricter than provider free-tier ceilings. If a task cannot be completed inside the free boundary, ECHO must change the execution strategy, reduce working-set size, shard the workload, use a defensible freely accessible source, or leave the node explicitly `OPEN` / `EXTERNAL_GATE_OPEN`.

The project must never solve a capacity, performance or evidence problem by silently enabling billing.

## Governance precedence

For execution decisions, this policy is a hard ancestor gate.

```text
ECHO-FREE-TIER-001
        ↓
MK-specific architecture / plan
        ↓
build / data / benchmark / integration
        ↓
certification evidence
```

A downstream node cannot override this policy implicitly. If a future requirement conflicts with it, the conflict must be surfaced explicitly before implementation and the dependent node remains open.

No certificate may claim PASS if its evidence requires an execution path that violates the boundary.

## GitHub Actions boundary

ECHO is a public repository. Standard GitHub-hosted runners are the only hosted runners authorized by default.

Allowed runner labels:

```text
ubuntu-latest
ubuntu-24.04
ubuntu-22.04
ubuntu-slim
```

Disallowed unless this policy is explicitly superseded by a future recorded governance decision:

```text
larger runners
GPU runners
paid marketplace compute
private-repository minute overages
external paid CI
```

Current standard public Linux runners provide a finite ephemeral SSD working volume. ECHO defines a lower engineering scratch ceiling of **10 GiB per job** to preserve operating-system/tooling headroom and prevent workflows from depending on the absolute provider maximum.

## Storage budget

ECHO must not use GitHub Actions Artifacts as a dataset lake.

Hard project budgets:

- retained GitHub artifact bytes across active ECHO runs: **<= 250 MB**;
- preferred maximum artifact produced by one workflow run: **<= 100 MB**;
- artifact retention: **1 day by default**;
- large public datasets: never persisted as GitHub artifacts;
- dataset bytes: process-and-delete inside the runner whenever possible;
- Git commits contain manifests, hashes, reports, source evidence and small fixtures only, not full corpora.

These project budgets intentionally remain below provider allowances and are the ECHO limits even when a provider temporarily allows more.

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

- `SONYC-UST`: execute shard-by-shard; no full-dataset residency.
- `SINGA:PURA`: execute only with a bounded extraction plan that keeps scratch <= 10 GiB.
- `FSD50K`: full multipart archive materialization is not a required release-safe dependency under standard hosted runners. Metadata and defensible per-asset acquisition may be used; full-corpus execution remains optional only if a future zero-cost method satisfies this boundary.
- `ESC-50`: research-only; execute only when the pinned free snapshot fits the boundary and source policy permits its intended use.
- `UrbanSound8K`: research-only and manual-provider gated; never purchase access.
- public per-asset gap pools: preferred for exact target-gap closure because they can be materialized incrementally.
- `ECHO Field Dataset`: user-controlled/authorized capture; does not require paid cloud storage and does not count toward development-source coverage.

## Model / benchmark execution model

The same invariant applies after corpus closure.

ECHO must prefer reproducible CPU-compatible or otherwise zero-cost execution paths for:

```text
benchmark A/B/C
feature extraction
training / fine-tuning
calibration
replay
latency/resource tests
Event Engine integration
certification evidence
```

If a candidate model can only be reproduced with paid compute, it is not eligible as a mandatory ECHO baseline under this policy. The project may keep such a model as research evidence only, while the certified path remains reproducible for $0.

## No hidden billing rule

Every external service introduced later must satisfy all of the following before use:

1. zero payment is required for the intended ECHO path;
2. hard free-tier limits are known;
3. ECHO's own project budget is below those limits;
4. no auto-upgrade/overage path is required;
5. a stop-line exists before provider billing can occur;
6. the service is replaceable without changing ECHO's domain contracts.

If any item fails, the service is `DENY_FOR_ECHO_DEFAULT`.

## Certification impact

All ECHO certificates inherit this policy.

`CERT-MK1-DF-CORPUS-001`, later benchmark/model certificates, integration evidence and future MK certificates may only become `CERTIFIED` when their required evidence can be produced within this boundary unless a future explicit governance decision supersedes the policy.

A zero-gap or performance requirement does **not** authorize paid infrastructure. If a node cannot close for free, the correct state is:

```text
status = OPEN or EXTERNAL_GATE_OPEN
reason = FREE_TIER_CAPACITY_OR_SOURCE_GATE
```

not a paid workaround, not a weakened engineering threshold and not fabricated evidence.

## Mandatory enforcement

The machine-readable authority is:

`configs/data_foundry/free_tier_boundary.v1.json`

Repository CI must fail closed when workflows drift outside allowed runners, retention policy or global billing flags.

Every new workflow or external provider introduced into ECHO must be evaluated against this policy before it is treated as part of the certified path.

## Invalidation / re-audit

This policy must be re-audited if:

- the repository becomes private;
- GitHub changes standard-runner or free-storage behavior materially;
- a workflow introduces a new provider;
- artifact retention/budgets change;
- a dataset acquisition path starts requiring payment;
- a new model requires paid compute to reproduce;
- any MK architecture proposes infrastructure that cannot stay under the declared boundary.

Re-audit does not itself authorize spending. Until an explicit superseding governance decision exists, `ECHO-FREE-TIER-001` remains in force.
