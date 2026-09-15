# MK1 Data Foundry Toolchain Recertification 004

**Certificate:** `CERT-MK1-DF-TOOLCHAIN-004`  
**Status:** `CERTIFIED`  
**Certified implementation baseline:** `ab8c47ba6aabb25390644954a2a06945ca7a81bb`  
**Global invariant:** `ECHO-FREE-TIER-001`

## Claim

This certificate recertifies the executable MK1 Data Foundry surface after the SONYC canonical-fingerprint contract and durable-persistence workflow changed materially. It supersedes `CERT-MK1-DF-TOOLCHAIN-003`, which is historical/invalidated for current HEAD.

The certified surface includes source/acquisition validation, bounded SONYC sharding, real-media probe evidence, canonical fingerprints, fingerprint-contract validation, exact-trigger-SHA execution, fail-closed durable persistence, canonical-ledger integration, corpus-closure readiness generation, and the model-entry guard.

## Exact technical evidence

The implementation baseline `ab8c47ba6aabb25390644954a2a06945ca7a81bb` passed:

- `MK1 Data Foundry CI` run `34922010529` — PASS on Python 3.10, 3.11 and 3.12;
- `ECHO Free-Tier Boundary` run `34922010518` — PASS;
- `ECHO Documentation Governance` run `34922010525` — PASS for the pre-recertification documentation baseline.

The persistence regression was also reviewed in PR #8, whose exact head `85723d1dc97822fc942091e0e1103a3d8df24312` passed Data Foundry CI `34921950754`, Free-Tier `34921950757`, and Documentation Governance `34921950814` before merge.

## Real SONYC execution evidence

`MK1 SONYC Free Materialization` run `34922010537` executed against the certified implementation baseline and passed the full empirical workflow:

```text
verified shards                 19 / 19 PASS
merge                           PASS
canonical fingerprint contract  PASS
probe_failures                  0
fingerprint_failures            0
durable persistence             PASS
```

Durable SONYC evidence was committed at `78fc019839f1c9dad1a58a70d439605d887361d7`.

The resulting evidence then propagated through:

```text
canonical ledger     c93ddb97902b3650921426aaf841473245c7908d
closure audits       311cc2001931d4cceedb90ab5d21f06e15fdf881
closure readiness    de1d31b280e9fad4a3764537aa75d7d72802adb7
```

This integration proves that the current Foundry machinery can consume the durable SONYC evidence without the previous `digest`/`vector_sha256` contract mismatch and without the previous dirty-worktree rebase defect.

## Certified fail-closed properties

The toolchain now enforces all of the following:

- every SONYC shard and merge execution is bound to the same trigger SHA;
- materialization uses real media and records probe/checksum evidence;
- canonical fingerprints use their actual schema fields, including `canonical_pcm_sha256` and `vector_sha256`;
- semantic overlap between target and confuser rows is deduplicated by acoustic asset identity for fingerprint coverage accounting;
- conflicting fingerprints for the same acoustic identity fail;
- evidence persistence refuses to proceed when `origin/main` has moved;
- dirty generated evidence is never rebased;
- bounded free-tier execution is mandatory;
- corpus/model entry remains blocked unless the named corpus certificate and all closure evidence pass.

## Current downstream empirical truth

The current readiness evidence at `de1d31b280e9fad4a3764537aa75d7d72802adb7` remains correctly `BLOCKED` with `modeling_allowed=false`.

The canonical ledger now has complete fingerprint coverage:

```text
ledger_entries             1164
fingerprint_count          1164
missing_fingerprint_count     0
```

However, real corpus gaps remain. In particular FIRE_ALARM and TIRE_SQUEAL positive floors are not met, TIRE_SQUEAL lacks hard negatives, and source-diversity gaps remain for several hard-negative pools. Therefore this toolchain certificate does not promote the corpus certificate.

## Non-claims

`CERT-MK1-DF-TOOLCHAIN-004` does **not** claim:

- that `EMP-DATASET-001` is closed;
- that `EMP-DATA-QUALITY-001` is closed;
- that global corpus dedup/group/split/coverage/freeze/reproducibility has passed;
- that `CERT-MK1-DF-CORPUS-001` is certified;
- that Benchmark A/B/C, model training, threshold calibration, replay or field-camera progression is authorized.

## Dependency consequence

```text
CERT-MK1-DF-TOOLCHAIN-004 = CERTIFIED
CERT-MK1-DF-SONYC-001     = CERTIFIED
        ↓
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
        ↓
close remaining corpus gaps
        ↓
CERT-MK1-DF-CORPUS-001
        ↓
model-entry gate
```

## Invalidation

This certificate becomes stale if Foundry source/acquisition/probe/fingerprint/dedup/group/split/coverage/freeze/readiness/model-entry semantics, certified tests/schemas/workflows, SONYC durable-persistence semantics, or `ECHO-FREE-TIER-001` change materially without the appropriate reruns and dependency review.
