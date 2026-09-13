# MK0 Gate Record

**Status:** `CERTIFIED`  
**Certificate:** `CERT-MK0-013`

## Gate matrix

| Gate | Result | Evidence class | Notes |
|---|---|---|---|
| G0-01 promise/scope | PASS | charter/owner | immutable promise |
| G0-02 source catalog | PASS | primary web evidence | expandable without reopening core |
| G0-03 related systems | PASS | project docs | operational precedent only |
| G0-04 dataset landscape | PASS | official releases | asset-level filtering still MK1 |
| G0-05 model landscape | PASS | papers/repos/docs | winner intentionally open |
| G0-06 target/PoC architecture | PASS | synthesis | multi-source contracts |
| G0-07 event lifecycle | PASS | design | raw != event != alert |
| G0-08 taxonomy v1 | PASS | ontology/data/domain synthesis | five targets |
| G0-09 license governance | PASS_WITH_MANIFEST_RULE | release/license evidence | exact BOM later |
| G0-10 camera | EXTERNAL_GATE_OPEN | hardware required | replay build unaffected |
| G0-11 benchmark protocol | PASS | scientific plan | A/B/C common protocol |
| G0-12 MK1 DoR | PASS_FOR_REPLAY_BUILD | dependency review | camera branch external |

## Why MK0 can close with empirical unknowns

Model winner, thresholds, runtime, capacity and field distance cannot truthfully be known before running MK1. The relevant MK0 responsibility is to define how those quantities will be measured and ensure the architecture can host the experiment.

## Stop conditions considered

MK0 would fail if taxonomy had no viable data path, if source abstraction depended on unavailable proprietary access, if test leakage was unavoidable, or if privacy/license constraints made the planned dataset/deployment impermissible.

## Consequence

```text
MK0 = CERTIFIED
MK1 replay build = READY_NOT_STARTED
MK1 real-camera = EXTERNAL_GATE_OPEN
MK2 = GATED_BY_MK1_EVIDENCE
```

## Invalidation

Use dependency-specific recertification rather than resetting all MK0. See `governance/CERTIFICATION-DAG.md`.