# MK0 Experiment Artifacts

**Status:** `SPECIFICATION_CERTIFIED`

## Purpose

Define the minimum envelope around any feasibility/benchmark artifact so later engineers can reproduce or reject it.

## Run manifest

```yaml
experiment_id: ...
question: ...
git_commit: ...
started_at_utc: ...
hardware: ...
os_runtime: ...
dependencies_lock_hash: ...
input_manifest_sha256: ...
model_checkpoint_sha256: ...
config_sha256: ...
seed: ...
```

## Result bundle

A valid result bundle contains machine-readable metrics where possible, raw prediction/event logs needed for recomputation, stderr/logs with secrets redacted, interpretation notes and failure/limitation notes.

## Artifact classes

`FEASIBILITY`: answers whether a path technically works.  
`BENCHMARK`: compares candidates under controlled protocol.  
`ROBUSTNESS`: changes noise/codec/domain condition.  
`RUNTIME`: measures latency/resource/capacity.  
`FIELD`: uses real hardware/site and therefore includes external-gate/provenance metadata.

## Integrity

Large datasets/models are not committed to Git merely for traceability. Their manifests record stable origin/version and hashes. If an upstream asset is mutable, cache/archive policy must preserve the exact tested bytes when legally permitted.

## Claim discipline

A result applies only to its recorded conditions. One model/hardware/config result cannot silently certify another environment.

## Invalidation

Missing inputs/hashes, discovered leakage, test-set tuning or changed preprocessing invalidates the relevant result bundle.