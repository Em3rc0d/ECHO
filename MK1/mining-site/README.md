# MK1 / Mining Site

**Status:** `READY_TO_ACCUMULATE_BUILD_EVIDENCE`

## Purpose

MK1 mining-site stores empirical evidence produced during implementation/benchmark/field integration while keeping it separate from normative design documents.

## Expected evidence

Dataset selection/admission reports, model comparison result bundles, camera probe/field evidence, MK0 handoff trace and later threshold/runtime/error-analysis records.

## Provenance rule

Every empirical file references build ID/commit, config, data/model hashes, environment and test protocol. Summaries link raw machine-readable artifacts where practical.

## No fabrication

Until a test runs, files describe required evidence and remain `PENDING`; they do not contain placeholder numbers presented as results.

## Promotion

Mining evidence feeds decision log, MK1 test reports and certification ledger. If evidence contradicts upstream architecture, the relevant upstream node reopens.

## Privacy

Field/audio artifacts follow permitted-use/retention policy and may be stored outside Git; the repo stores manifests/hashes/results.