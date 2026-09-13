# MK0 / Test

**Status:** `CERTIFIED`

## Purpose

MK0 test validates the **quality of the research/design evidence**, not classifier performance. It checks that claims have sources, protocols are reproducible, unresolved facts are not invented and the next milestone has a defensible Definition of Ready.

## Artifacts

`CLAIM-CHECKLIST.md` audits epistemic status. `EVIDENCE-VALIDATION.md` defines source/provenance review. `FEASIBILITY-TESTS.md` describes what must be empirically tested later. `MK0-GATE.md` and `MK0-CERTIFICATE.md` record the certification boundary.

## Key distinction

Protocol readiness != test result. MK0 can certify “we know how to compare models fairly” while leaving “which model wins?” open for MK1.

## Pass condition

All architecture-changing unknowns are closed, isolated as an experiment or marked external; no dependent artifact relies on an untraceable claim; MK1 replay build can proceed without core redesign.

## Invalidation

New contradictory primary evidence, license changes, semantic scope changes or leakage in assumptions can invalidate only the affected certificate subgraph.