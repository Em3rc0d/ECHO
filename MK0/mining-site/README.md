# MK0 / Mining Site

**Status:** `CERTIFIED_EVIDENCE_REPOSITORY`

## Purpose

The mining site preserves externally sourced facts and provenance separately from ECHO decisions. It is where another engineer or model can inspect what was actually found, which release/document supported it and how it was interpreted.

## Evidence classes

`PRIMARY_DOC` official standards/product/model documentation.  
`PAPER` original research publication.  
`OFFICIAL_RELEASE` dataset/repository release.  
`RELATED_SYSTEM` operational precedent.  
`NORMATIVE` legal/standards material.  
`FIELD` future measurement from real ECHO hardware/site.

## Artifacts

`EVIDENCE-LEDGER.md` indexes claims. `SOURCES-MODELS.md`, `SOURCES-DATASETS.md` and `SOURCES-STREAMING-PUBSUB.md` group source families. `RELATED-SYSTEMS.md` records comparable projects. `WEB-AUDIT-2026-09-13.md` is the dated audit snapshot.

## Rule

A source does not become a product decision automatically. Quarries synthesize multiple evidence nodes and design/architecture files freeze decisions with rationale.

## Provenance

Record canonical URL/release/version where available, what exact claim is supported and any licensing caveat. Avoid using a secondary blog when primary docs exist.

## Invalidation

If a release, license or specification changes materially, mark dependent evidence stale and review the certificate DAG rather than silently editing conclusions.