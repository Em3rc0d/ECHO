# MK2 Release Artifacts

**Status:** `SPECIFICATION`

## Required bundle

```text
application/container digest
source commit
SBOM/dependency lock
model/checkpoint digest
preprocessing/calibration/EventEngine config digests
taxonomy/schema/config versions
deployment profile
migration scripts/runbook
license/notices inventory
security scan summary
quality/runtime/load/soak/resilience reports
field-holdout report
rollback artifact/reference
provenance/attestation
known limitations/release notes
```

## Integrity

Artifacts reference each other through a release manifest; changing any component after certification creates a new release candidate.

## Storage

Large binaries/models live in appropriate artifact/model registry with immutable digest, not necessarily Git. Git stores manifests, policies and references.

## Promotion

Only artifacts listed in the candidate manifest may be deployed. Ad hoc model/config replacement invalidates release evidence.

## Retention

Keep enough prior certified artifacts to reproduce/rollback supported releases under policy.

## Invalidation

Any post-certification change to digest-bearing artifact invalidates the release certificate.