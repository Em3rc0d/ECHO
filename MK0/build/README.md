# MK0 / Build

**Status:** `RESEARCH_ARTIFACTS_ONLY / PRODUCT_CODE_NOT_APPLICABLE`

## Purpose

MK0 is primarily a research/design milestone. Its build stage materializes research tooling/specification artifacts needed to make evidence reproducible; it is not the product implementation stage.

## Allowed artifacts

Manifest/schema prototypes, benchmark experiment definitions, reproducibility notes, evidence hashes and small disposable feasibility probes may exist here when they serve MK0 validation.

## Not allowed

A premature production pipeline, hardcoded single-camera application, arbitrary thresholds or a “demo” that bypasses unresolved design decisions cannot be used to claim MK0 completion.

## Gate behavior

MK0 build artifacts consume certified brainstorming/design/arch/plan inputs and must be testable in `MK0/test`. Product implementation belongs to MK1 after `CERT-MK1-READY-001`.

## Output

Evidence formats and experiment artifact requirements that MK1 can implement without reinterpreting the research.

## Invalidation

If research tooling embeds a material design assumption that later changes, regenerate/revalidate the artifact rather than carrying it forward silently.