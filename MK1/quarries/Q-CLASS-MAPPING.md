# Quarry — Class Mapping

**Status:** `POLICY_CERTIFIED / ASSET REVIEW EMPIRICAL`

## Purpose

Map heterogeneous dataset labels/assets into the five ECHO targets without relying on string similarity.

## Mapping states

`EXACT`, `NARROWER`, `BROADER`, `AMBIGUOUS`, `NEGATIVE`, `UNUSABLE`.

For each source label document ontology definition, ECHO definition, overlap, exclusions and examples requiring manual review.

## Critical cases

Generic `Shatter` may include non-glass brittle materials; generic `Alarm` may include security/clock/vehicle sounds and cannot automatically map to `FIRE_ALARM`; broad squeal labels may include machinery rather than tire friction.

## Asset review

Ambiguous broad source classes require clip-level review/metadata evidence or exclusion. Review decisions are recorded with label provenance and reviewer/version.

## Coexistence

Because targets are multi-label, mapping does not remove a second valid target when both are audible. Negative labels may coexist with target examples as background context.

## Validation

Audit random/priority samples per mapped source class and inspect high-loss/error examples after first model. Mapping errors are data problems, not automatically model failures.

## Output

Versioned label mapping consumed by dataset manifest and model head.

## Invalidation

Taxonomy/source ontology/release change creates a new mapping version.