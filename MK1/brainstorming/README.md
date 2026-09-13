# MK1 / Brainstorming

**Status:** `CLOSED_FOR_BUILD`

## Purpose

MK1 brainstorming narrows the certified research landscape into a minimal vertical that is valuable enough to test the ECHO promise and small enough to finish without hiding unresolved complexity.

## Core questions

What must the first build prove? Which features are essential to produce trustworthy evidence? Which concerns can be deferred to MK2 without forcing a rewrite? How can one physical camera coexist with a logically multi-source architecture?

## Artifacts

`SCOPE-CUT.md` defines IN/OUT. `PRODUCT-HYPOTHESES.md` captures what the build must test. `DEMO-STORY.md` describes a truthful demonstration that mirrors the real pipeline rather than a hand-picked classifier clip.

## Synthesis

The first build is not “train YAMNet”. It is a full event pipeline with deterministic replay, model comparison, temporal aggregation, source identity and delivery. Camera integration is an adapter branch, not a hard dependency for core development.

## Exit

Brainstorming is closed because all remaining high-impact uncertainty is represented as an experiment or external gate and design can specify contracts without guessing.

## Invalidation

Reopen only if the MK1 objective or frozen taxonomy changes materially.