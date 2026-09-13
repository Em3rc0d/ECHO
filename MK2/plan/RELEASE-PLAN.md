# MK2 Release Plan

**Status:** `SPECIFIED / RELEASE GATED`

## Release bundle

Application artifact/container, model/calibration/EventEngine bundle, schema/config versions, dependency lock/SBOM, native tool/broker versions as applicable, migrations, deployment manifest, notices/licenses, test reports, provenance/attestation and known limitations.

## Pre-release gates

Frozen SLO profile; MK1 dependencies valid; capacity/load/soak pass; resilience/chaos pass; model regression/field holdout pass; security/privacy checks; rollback test; external gates required by declared deployment closed.

## Release candidate

Immutable RC deployed to staging under production-like source/replay load. No last-minute configuration change outside the manifest.

## Promotion

Controlled rollout/canary where possible with health/SLO observation. Promotion stops on critical regression or unexplained alert behavior.

## Release notes

State supported deployment profile, model/taxonomy/schema versions, measured envelope, known limitations, security/privacy considerations and migration steps.

## Post-release

Monitor source health, false-alert trends, latency/capacity, delivery and model drift; preserve regression corpus and prior rollback artifact.

## Failure

A failed gate delays release or explicitly changes scope/SLO through governance; it is never converted to PASS by documentation wording.