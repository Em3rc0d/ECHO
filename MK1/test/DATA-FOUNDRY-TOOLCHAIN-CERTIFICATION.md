# MK1 Data Foundry — Toolchain Certification

**Certificate:** `CERT-MK1-DF-TOOLCHAIN-001`  
**Status:** `CERTIFIED`  
**Certified code baseline:** `2c4d4c2aae3e13de84680f65a79d5bb69301e18c`  
**GitHub Actions run:** `34742947903`  
**Date:** 2026-09-13

## 1. Claim

This certificate covers the **executable Data Foundry toolchain** required to transform declared source releases into a reproducible, auditable benchmark corpus candidate. It certifies engineering behavior and synthetic end-to-end execution; it does not certify a real downloaded corpus that has not yet been materialized.

## 2. Certified path

```text
release registry / acquisition verification
        ↓
source-specific metadata intake
        ↓
canonical RawAssetCandidate JSONL
        ↓
technical audio probe + SHA-256
        ↓
license/use-policy admission
        ↓
semantic mapping + governed manual review
        ↓
quality/quarantine
        ↓
group identity + exact/perceptual duplicate screening
        ↓
protected split assignment
        ↓
asset/split/coverage/dedup/quarantine manifests
        ↓
frozen dataset manifest
        ↓
validated benchmark split reader
```

## 3. Gate coverage

| Gate | Toolchain evidence | Result |
|---|---|---|
| DF-G0 source registry | versioned semantic and acquisition registries + validation | PASS |
| DF-G1 acquisition/provenance | acquisition plan + publisher-checksum verifier | PASS |
| DF-G2 rights | versioned license/use policy, fail-closed unknown rights | PASS |
| DF-G3 semantic mapping/review | label mapping + review evidence contract | PASS |
| DF-G4 technical integrity | local SHA-256 + WAV/ffprobe technical probe + corrupt-audio quarantine | PASS |
| DF-G5 grouping/dedup | group leakage, exact duplicate, registered near-duplicate and identical-byte label-conflict guards | PASS |
| DF-G6 protected splits | upstream split preservation + deterministic group fallback + field-holdout isolation | PASS |
| DF-G7 frozen evidence bundle | canonical asset/split manifests + coverage/dedup/quarantine reports + dataset manifest hashes | PASS |
| DF-G8 benchmark handoff | frozen-bundle hash/identity validator + manifest-only split enumeration | PASS |

## 4. CI evidence

Workflow `.github/workflows/mk1-data-foundry-ci.yml` ran against the certified baseline on Python **3.10, 3.11 and 3.12**. All three matrix jobs completed successfully in run `34742947903`.

The Python 3.11 job executed **42 tests** and ended `OK`. Test families covered:

- acquisition registry/checksum behavior;
- FSD50K, SONYC-UST, SINGA:PURA, ESC-50 and UrbanSound8K adapters;
- admission and rights policy;
- semantic mapping and review decisions;
- deterministic candidate/asset manifests;
- group-aware splitting;
- exact and registered-near duplicate leakage;
- exact-byte label conflicts;
- PCM-WAV perceptual-screening fingerprint behavior;
- technical audio probes and corrupt-audio quarantine;
- synthetic admission -> freeze -> frozen-bundle validation -> benchmark split handoff.

## 5. Stop-the-line evidence

During hardening, CI initially failed because two synthetic audio fixtures produced the same gain-normalized near-duplicate fingerprint while assigned to different protected splits. The failure was not bypassed. The fixtures were corrected to represent genuinely different temporal envelopes and the full matrix was rerun to green.

This is evidence that the duplicate-leakage guard is active rather than documentary only.

## 6. Reproducibility and provenance

The toolchain binds corpus evidence to versioned source registry, acquisition registry, license policy, label mapping, review decisions, split policy, local file hashes, group identities and frozen manifest hashes. Benchmark consumers validate those identities before enumerating train/validation/test rows.

No raw audio, credentials or multi-gigabyte dataset archives are committed to Git.

## 7. Explicit non-claims

This certificate does **not** claim:

- final admitted counts/durations/group diversity for real releases;
- that `FIRE_ALARM` or `TIRE_SQUEAL` sourcing gaps are solved;
- absence of all near duplicates in external media before running the real corpus;
- model quality, calibration, thresholds or field performance;
- camera/RTSP compatibility;
- `CERT-MK1-DF-CORPUS-001` completion.

Those claims require actual source-media execution and remain represented by empirical/external nodes rather than being inferred.

## 8. Downstream authorization

The certified toolchain authorizes the next operation:

```text
EXEC-DATA-001
  acquire declared source media on controlled storage
      -> run G0..G8 on real releases
      -> EMP-DATASET-001
      -> EMP-DATA-QUALITY-001
      -> CERT-MK1-DF-CORPUS-001
      -> A/B/C model benchmark
```

Model training may not bypass the frozen-manifest handoff.

## 9. Invalidation

`CERT-MK1-DF-TOOLCHAIN-001` becomes `INVALIDATED` if a material change alters source/acquisition semantics, rights policy, taxonomy/mapping, manual-review contract, technical probe rules, grouping/splitting, duplicate guards, manifest hashing, benchmark handoff validation or CI coverage without re-running the affected certification suite.
