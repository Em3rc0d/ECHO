# MK1 / Mining Site

**Status:** `ACTIVE_EMPIRICAL_EVIDENCE / CORPUS_CLOSURE_RESEARCH_REGISTERED`

## Purpose

MK1 mining-site stores empirical evidence and research syntheses produced during implementation, corpus closure, benchmark and field integration while keeping evidence separate from normative design documents.

## Expected evidence

Dataset selection/admission reports, publisher/source materialization evidence, corpus closure research, model comparison result bundles, camera probe/field evidence, MK0 handoff trace and later threshold/runtime/error-analysis records.

Current corpus-closure research synthesis:

`CORPUS-CLOSURE-DEEP-RESEARCH-2026-09-13.md`

Machine-generated source materialization evidence lives under:

`materialization/`

## Provenance rule

Every empirical file references build ID/commit, config, data/model hashes, environment and test protocol where applicable. Summaries link raw machine-readable artifacts where practical.

Research synthesis must distinguish facts/evidence from inference, hypothesis, decision and target state. A research recommendation does not become empirical PASS until the required execution produces evidence.

## No fabrication

Until a test runs, files describe required evidence and remain `PENDING` / `OPEN`; they do not contain placeholder numbers presented as results.

A successful workflow does not by itself certify a downstream node unless the evidence corresponds to the exact commit/policy/data identity being certified.

## Promotion

Mining evidence feeds decision logs, MK1 build/test reports and the certification ledger. If evidence contradicts upstream architecture, the relevant upstream node reopens according to the dependency DAG.

Corpus evidence may promote to `CERT-MK1-DF-CORPUS-001` only through the normative closure plan in:

`../build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md`

## Global execution boundary

All empirical/research execution inherits `ECHO-FREE-TIER-001`.

Research may identify paid techniques or services as context, but they cannot become mandatory ECHO execution dependencies while that policy remains frozen. If a node cannot close under the boundary, it stays `OPEN` / `EXTERNAL_GATE_OPEN` rather than weakening evidence quality.

## Privacy

Field/audio artifacts follow permitted-use/retention policy and may be stored outside Git; the repo stores manifests, hashes, compact reports and evidence rather than uncontrolled raw recordings.
