# ECHO Documentation Standard

## Purpose

ECHO is intentionally **documentation-first**. A Markdown file is not considered complete merely because it names a problem or lists questions. Every substantive artifact must preserve enough context for a human engineer or another model to reconstruct **why a decision exists, what evidence supports it, what remains unknown, and what would invalidate it**.

README files may stay concise because their purpose is navigation. Research, design, architecture, planning, quarry, risk, benchmark and certification artifacts must be self-contained.

## Required structure for substantive artifacts

Every non-index artifact SHOULD contain, when applicable:

1. **Purpose / question** — what uncertainty or decision this file owns.
2. **Scope and non-scope** — what is intentionally not answered here.
3. **Upstream dependencies** — artifacts/evidence this document relies on.
4. **Definitions** — terms that could be interpreted differently.
5. **Evidence** — primary sources, measurements, datasets or experiments.
6. **Alternatives considered** — not just the selected path.
7. **Decision / current position** — `OPEN`, `CANDIDATE`, `CLOSED`, `CERTIFIED`, `EXTERNAL_GATE_OPEN`.
8. **Rationale** — why the current position follows from the evidence.
9. **Risks / failure modes** — how the decision can fail.
10. **Validation plan** — how claims are tested rather than assumed.
11. **Outputs / downstream consumers** — which later artifacts use the result.
12. **Invalidation conditions** — upstream changes or evidence that force re-review.
13. **Provenance / references** — URLs, repo paths, paper IDs, dataset releases, hashes when applicable.

## Evidence language

Use these tags consistently:

- `FACT/EVIDENCE`: directly supported by a source or measurement.
- `INFERENCE`: derived logically from evidence but not directly stated by a source.
- `HYPOTHESIS`: requires experiment.
- `DECISION`: frozen engineering choice within a stated scope.
- `TARGET`: desired future value, never presented as measured performance.

## Depth rule

There is no arbitrary minimum word count. The rule is semantic completeness. A 300-byte file that only asks questions is a **stub**, not a finished quarry. A substantive document must contain enough detail that a reader can answer:

```text
What are we deciding?
What evidence do we have?
What alternatives exist?
What did we choose and why?
What is still unknown?
How will it be tested?
What breaks if this assumption changes?
```

Short files are acceptable only for navigation, machine-readable manifests, tiny schemas or explicit placeholders marked `STUB / NOT_CERTIFIED`.

## Quarry standard

A quarry is a research workstream, not a checklist. Each quarry must preserve:

```text
question -> evidence -> synthesis -> candidate decision -> validation -> closure condition
```

A quarry may be `CERTIFIED_FOR_<SCOPE>` while still containing empirical outputs that belong to a later MK. Example: MK0 may certify the **benchmark protocol**, while model winner and thresholds remain outputs of MK1.

## Certification interaction

Certification does not mean “all uncertainty disappeared”. It means all uncertainty that can change the next stage's architecture is either:

- closed by evidence;
- converted into a controlled experiment;
- or explicitly isolated as `EXTERNAL_GATE_OPEN`.

Any material edit to a certified upstream artifact requires dependency review under `governance/CERTIFICATION-DAG.md`.

## Review checklist

Before marking a knowledge artifact complete:

- [ ] It contains evidence, not only conclusions.
- [ ] Facts and hypotheses are distinguishable.
- [ ] Alternatives and rejected options are recorded.
- [ ] Failure modes are explicit.
- [ ] Metrics/validation are defined before implementation.
- [ ] External dependencies are named.
- [ ] No target or benchmark result is invented.
- [ ] Sources and provenance are traceable.
- [ ] Downstream dependencies are listed.
- [ ] Invalidation conditions are documented.

This standard applies to MK0, MK1 and MK2.