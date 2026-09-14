# ECHO Documentation Standard

**Status:** `FROZEN_DOCUMENTATION_GOVERNANCE`  
**Scope:** all ECHO milestones, research, design, architecture, planning, build, test, evidence and certification artifacts.  
**Inherited invariant:** `ECHO-FREE-TIER-001`.

## Purpose

ECHO is intentionally **documentation-first**. Documentation is not decorative support for implementation; it is an upstream engineering artifact that must be coherent enough to constrain implementation, testing and certification.

A Markdown file is not considered complete merely because it names a problem or lists questions. Every substantive artifact must preserve enough context for a human engineer or another model to reconstruct **why a decision exists, what evidence supports it, what remains unknown, how it is validated, what depends on it, and what would invalidate it**.

README files may stay concise because their purpose is navigation. Research, design, architecture, planning, quarry, risk, benchmark and certification artifacts must be self-contained.

## Documentation-first execution rule

For every material project node, the authoritative order is:

```text
research / evidence
        ↓
documented decision or controlled hypothesis
        ↓
design contract
        ↓
architecture
        ↓
execution plan + acceptance criteria
        ↓
build
        ↓
test evidence
        ↓
certificate
```

No implementation result may retroactively invent its own requirements. If implementation reveals that a documented assumption is wrong, the affected documentation node is reopened first, dependents are reviewed through `governance/CERTIFICATION-DAG.md`, and only then is the build path changed.

## Hard certification precondition

A project node is **not eligible for `CERTIFIED`** unless its required documentation is itself current and reviewable.

For a certificate to close, the reviewer must be able to identify:

```text
claim and scope
upstream certified inputs
current normative documentation
acceptance criteria
implementation/build identity when applicable
test or empirical evidence when applicable
known non-claims
remaining external gates
invalidation conditions
ECHO-FREE-TIER-001 compatibility
```

A green test suite cannot compensate for stale architecture or contradictory policy. Strong documentation cannot compensate for missing empirical evidence. Both are required where the claim depends on both.

## Required structure for substantive artifacts

Every non-index authoritative artifact MUST contain the applicable subset of:

1. **Purpose / question** — what uncertainty, contract or decision the file owns.
2. **Scope and non-scope** — what is intentionally not answered here.
3. **Status / epistemic state** — e.g. `OPEN`, `CANDIDATE`, `CLOSED`, `CERTIFIED`, `INVALIDATED`, `EXTERNAL_GATE_OPEN`.
4. **Upstream dependencies** — artifacts/evidence this document relies on.
5. **Definitions** — terms that could be interpreted differently.
6. **Evidence** — primary sources, measurements, datasets or experiments.
7. **Alternatives considered** — not just the selected path.
8. **Decision / current position** — the actual engineering position within its scope.
9. **Rationale** — why the current position follows from evidence.
10. **Risks / failure modes** — how the decision can fail.
11. **Validation / acceptance plan** — how claims are tested rather than assumed.
12. **Outputs / downstream consumers** — which later artifacts depend on this result.
13. **Invalidation conditions** — changes or evidence that force re-review.
14. **Provenance / references** — URLs, repo paths, paper IDs, dataset releases, hashes or CI run IDs when applicable.
15. **Boundary compatibility** — when execution is involved, how the path stays under `ECHO-FREE-TIER-001`.

A section may be omitted when genuinely not applicable, but the absence may not hide an unresolved requirement.

## Evidence language

Use these tags consistently when they materially clarify certainty:

- `FACT/EVIDENCE`: directly supported by a source or measurement.
- `INFERENCE`: derived logically from evidence but not directly stated by a source.
- `HYPOTHESIS`: requires experiment.
- `DECISION`: frozen engineering choice within a stated scope.
- `TARGET`: desired future value, never presented as measured performance.

Empirical counts, quality metrics, latency, model performance, capacity or field behavior must never be promoted from `TARGET`/`HYPOTHESIS` to `FACT/EVIDENCE` without a traceable execution artifact.

## Cross-document coherence rule

Documentation quality is not only per-file depth. Authoritative documents must agree with each other on current project truth.

At minimum, changes to a critical node require coherence review against:

```text
PROJECT-CHARTER.md
CURRENT-STATE.md
governance/CERTIFICATION-LEDGER.md
governance/CERTIFICATION-DAG.md
governance/FREE-TIER-BOUNDARY.md
phase-specific design / architecture / plan / test documents
machine-readable policy/config when one exists
```

A contradiction between an authoritative document and a newer frozen policy is a documentation gate failure until resolved. Historical documents may preserve superseded facts only when clearly marked historical/superseded and not presented as current execution guidance.

## Machine-readable alignment rule

When a Markdown policy has a machine-readable counterpart, they form one governed contract. Examples include taxonomy, source registry, coverage policy, split policy, rights policy, dataset certification and free-tier boundary.

The documentation certificate fails if the prose and machine-readable authority disagree on a material rule.

## Depth rule

There is no arbitrary minimum word count. The rule is semantic completeness. A short file that only asks questions is a **stub**, not a finished quarry. A substantive document must contain enough detail that a reader can answer:

```text
What are we deciding?
What evidence do we have?
What alternatives exist?
What did we choose and why?
What is still unknown?
How will it be tested?
What blocks downstream work?
What breaks if this assumption changes?
```

Short files are acceptable only for navigation, machine-readable manifests, tiny schemas or explicit placeholders marked `STUB / NOT_CERTIFIED` or equivalent.

## Quarry standard

A quarry is a research workstream, not a checklist. Each quarry must preserve:

```text
question -> evidence -> synthesis -> candidate decision -> validation -> closure condition
```

A quarry may be `CERTIFIED_FOR_<SCOPE>` while still containing empirical outputs that belong to a later MK. Example: MK0 may certify the benchmark **protocol**, while model winner and thresholds remain outputs of MK1.

## Documentation certificate lifecycle

A documentation certificate is scoped to a repository documentation corpus or explicitly defined delta.

```text
new substantive Markdown
or material rewrite
or new machine-readable policy affecting documented truth
        ↓
current documentation certificate becomes stale for current HEAD
        ↓
delta/full audit
        ↓
contradictions fixed
        ↓
new documentation certificate
```

Historical documentation certificates remain immutable evidence for their original repository state. They are never silently stretched to cover later files.

## Certification interaction

Certification does not mean “all uncertainty disappeared”. It means all uncertainty that can change the next stage's architecture is either:

- closed by evidence;
- converted into a controlled experiment with defined acceptance criteria;
- or explicitly isolated as `OPEN` / `EXTERNAL_GATE_OPEN` without being misrepresented as complete.

Any material edit to a certified upstream artifact requires dependency review under `governance/CERTIFICATION-DAG.md`.

## Documentation gate checklist

Before an authoritative node can be treated as documentation-complete:

- [ ] It contains evidence, not only conclusions.
- [ ] Facts, inferences, hypotheses, decisions and targets are distinguishable where needed.
- [ ] Alternatives and rejected options are recorded when material.
- [ ] Failure modes are explicit.
- [ ] Metrics/validation are defined before authoritative empirical claims.
- [ ] External dependencies and external gates are named.
- [ ] No target, benchmark result or corpus property is invented.
- [ ] Sources and provenance are traceable.
- [ ] Downstream dependencies are listed or reconstructible.
- [ ] Invalidation conditions are documented.
- [ ] Current-state and certification ledger agree with the artifact.
- [ ] Machine-readable policy agrees with prose when both exist.
- [ ] The execution path respects `ECHO-FREE-TIER-001`.
- [ ] No stale superseded execution instruction is presented as current truth.

This standard applies to every ECHO MK and every later milestone unless explicitly superseded by a recorded governance decision.