# MK2 Release Gate

**Status:** `GATED`

## Required evidence

- valid MK1 upstream certificate;
- frozen production deployment/SLO profile;
- reproducible application/model/config release bundle;
- capacity and load/soak PASS;
- resilience/fault/chaos PASS for required scenarios;
- model/field regression PASS;
- schema/config/model migration and rollback tested;
- security/privacy checks PASS;
- dependency/SBOM/license/notices complete;
- observability and incident runbooks validated;
- required external hardware/network/authorization gates closed.

## Scope declaration

The certificate names exact supported hardware/model/source range/environment assumptions. It does not certify every possible camera/site.

## Conditional failure

A non-blocking optional feature may be excluded from release scope with explicit documentation. A core promise/SLO failure cannot be waived silently.

## Evidence integrity

All reports reference release candidate digest. Rebuilding/reconfiguring after test creates a new candidate requiring the applicable subset of tests.

## Decision

Only test evidence and governance can move this gate to `CERTIFIED`; documentation completeness alone cannot.