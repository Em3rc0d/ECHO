# MK2 CI/CD Plan

**Status:** `SPECIFIED`

## CI stages

Static/lint/type checks where applicable -> unit/contract tests -> schema/config validation -> deterministic replay regression -> model artifact/manifest checks -> integration/MQTT tests -> security/dependency scans -> package/container build -> provenance/attestation.

Heavy ML/load/field suites may run scheduled or release-gated rather than every commit, but release cannot bypass required evidence.

## Artifact identity

CI records git SHA, dependency lock, container/binary hashes, model/config/schema versions and SBOM. Build artifacts are immutable/content-addressed where practical.

## Model separation

Code CI and model-release pipeline interact through a registry/manifest. A new code build must validate compatibility with active model/schema; a new model must pass regression under supported runtime.

## Deployment stages

Development -> staging/replay -> canary/limited source group -> production profile. Promotion uses gates, not only successful build.

## Secrets

CI uses secret store; logs/artifacts redact values. No camera credentials in fixtures.

## Rollback

Retain prior certified application/model/config bundle. Deployment health/SLO checks can halt/rollback promotion.

## Evidence

CI output feeds certification DAG rather than being treated as disposable console logs.