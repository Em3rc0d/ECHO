# MK2 / Build

**Status:** `GATED_BY_MK1_AND_MK2_DESIGN`

## Purpose

Materialize production hardening after MK1 evidence freezes SLO/deployment decisions. This folder specifies release/runtime artifacts before implementation begins.

## Expected work

Scale/runtime changes, resilient service packaging, production config/secrets, model registry/release, observability, secure broker/store integration, migration/rollback tooling, SBOM/provenance and deployment manifests.

## Anti-pattern

Do not implement distributed infrastructure or HA before the target profile requires it. Build remains gated until design/plan is evidence-backed.

## Reproducibility

Every production artifact is versioned/hashable and associated with source code/model/config/schema/BOM identities.

## Output

Release candidates consumed by MK2 load/soak/resilience/security/release tests.