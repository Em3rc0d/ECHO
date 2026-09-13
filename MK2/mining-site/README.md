# MK2 / Mining Site

**Status:** `EVIDENCE_DESTINATION / AWAITS MK2 EXECUTION`

## Purpose

Store production-stage evidence: capacity/benchmark history, field evidence across releases, incident learnings and exact third-party/license inventories.

## Artifacts

`BENCHMARK-HISTORY.md` tracks comparable release/model measurements. `FIELD-EVIDENCE.md` tracks real source/site operating evidence. `INCIDENT-EVIDENCE.md` converts incidents into regression/risk knowledge. `LICENSE-INVENTORY.md` records release-specific third-party assets.

## Provenance

Every record names release/model/config/hardware/time range and source of truth. Large logs/media remain outside Git under governed storage; this folder stores summaries/manifests/hashes.

## Relationship to design

Mining-site is evidence, not aspirational architecture. Findings can invalidate SLOs, scale decisions or model releases through the certification DAG.

## Privacy

Operational evidence must minimize raw audio/personal data and follow retention/access policy.