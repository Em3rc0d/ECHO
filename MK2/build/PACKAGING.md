# MK2 Packaging

**Status:** `TARGET_SPEC`

## Goal

Produce reproducible deployable artifacts with explicit native/ML dependencies and supply-chain metadata.

## Artifact options

Container image preferred for reproducible service packaging where deployment supports it; system package/virtual environment remains possible for edge hosts. Whichever path is chosen, versions/hashes are captured.

## Included vs external

Decide explicitly whether FFmpeg/GStreamer/Mosquitto are bundled or external services/packages. Bundling changes licensing/SBOM/security responsibilities.

## Model artifacts

Model bundle can be packaged separately from app to allow independent promotion/rollback; app verifies compatible schema/runtime and hash.

## Security

Minimal base image, non-root where feasible, no embedded credentials, read-only filesystem where practical, resource limits and signed/hashable image/artifacts.

## Reproducibility

Build from locked dependencies and recorded base-image digest; output image/package digest enters release manifest.

## Validation

Fresh-machine/staging install, startup, dependency/provenance scan and rollback to prior package.