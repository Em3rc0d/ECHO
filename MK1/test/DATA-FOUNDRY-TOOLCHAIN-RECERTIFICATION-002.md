# MK1 Data Foundry — Toolchain Recertification 002

**Certificate:** `CERT-MK1-DF-TOOLCHAIN-002`  
**Status:** `CERTIFIED`  
**Supersedes for current engineering baseline:** `CERT-MK1-DF-TOOLCHAIN-001`  
**Certified code/config/test baseline:** `be75a4323ec67f7c9528cbdbf6a06a8524494501`  
**GitHub Actions run:** `34800084225`  
**Date:** 2026-09-13  
**Inherited boundary:** `ECHO-FREE-TIER-001`

## 1. Trigger

`CERT-MK1-DF-TOOLCHAIN-001` was valid for the earlier baseline `2c4d4c2aae3e13de84680f65a79d5bb69301e18c`. Since that certificate, the Data Foundry gained material source-policy, release-safe coverage, publisher-snapshot and materialization enforcement code/tests.

The original certificate explicitly requires revalidation after material changes to source/acquisition semantics, rights policy, dedup/split/manifest behavior or CI coverage. This document records that revalidation instead of silently stretching the older certificate.

## 2. Certified claim

This certificate covers the **current executable engineering toolchain** needed to transform declared source evidence/candidates into a governed, fail-closed corpus candidate and benchmark-facing frozen bundle.

It certifies software/config/schema/test behavior only. It does **not** certify the real MK1 corpus, final cross-format near-duplicate policy, model performance or field behavior.

## 3. Current certified surface

At the certified baseline, the toolchain covers:

```text
source registry validation
publisher/acquisition evidence
source-policy enforcement
metadata adapters/intake
real-byte technical probe + SHA-256
license/use admission
semantic mapping + governed reviews
release-safe coverage policy
quality/quarantine
exact duplicate / registered near-duplicate / label-conflict guards
group-aware split behavior
field-holdout exclusion
frozen manifest/report bundle
bundle validation
benchmark-facing split enumeration
```

The release-safe path cannot omit source certification or coverage policy.

## 4. CI evidence

Run `34800084225` completed successfully on:

```text
Python 3.10  PASS
Python 3.11  PASS
Python 3.12  PASS
```

The Python 3.11 job executed **67 tests** and completed `OK`.

The run also passed explicit steps for:

```text
compile source/tests
validate registries/policies/schemas
validate Foundry source registry
validate release-safe coverage policy
acquisition registry smoke test
full Foundry unit + synthetic E2E suite
```

The checked-out SHA recorded by the CI job was exactly:

```text
be75a4323ec67f7c9528cbdbf6a06a8524494501
```

## 5. Important test evidence added since 001

The current suite includes fail-closed checks for:

- incomplete/tiny `release_safe` corpus coverage;
- missing source-certification policy;
- missing release-safe coverage policy;
- research-only or incompatible rights entering release-safe freeze;
- field holdout being used to hide development gaps;
- generic background being used instead of explicit hard negatives;
- missing technical provenance;
- exact duplicate failures;
- group leakage;
- registered near-duplicate cross-split leakage;
- publisher snapshot/checksum drift;
- conditional/unknown source-policy states;
- deterministic group split behavior.

## 6. Relationship to Corpus Foundry Closure

The deep-research/closure plan introduced stricter final-corpus requirements that are intentionally **not fabricated as already implemented**.

In particular, final `CERT-MK1-DF-CORPUS-001` still requires closure of:

```text
canonical global admitted asset ledger
materialized/admitted hard-negative evidence
cross-format/transcode-aware near-duplicate hardening + fixture validation
global recording-family audit
coverage/diversity PASS on real admitted corpus
first freeze validation
second clean freeze identity comparison
```

Therefore:

```text
CERT-MK1-DF-TOOLCHAIN-002 = CERTIFIED
CERT-MK1-DF-CORPUS-001    = OPEN
```

There is no contradiction: the toolchain certificate proves the current executable foundation; the corpus certificate has a stricter empirical/integration predicate.

## 7. Free-tier evidence

The certified path is compatible with the project-level zero-cost architecture. Dataset execution is bounded/sharded and raw corpora are not required as durable GitHub artifacts.

No paid runner, paid GPU, paid dataset source, paid API or automatic-overage path is authorized by this certificate.

## 8. Code-equivalence note after certified baseline

At the time this certificate was authored, commits after `be75a4323ec67f7c9528cbdbf6a06a8524494501` changed documentation and materialization evidence only; they did not alter the certified `src/`, `tests/`, machine-readable Foundry policy/schema surface or Data Foundry CI workflow.

A later change to any certified code/config/schema/test/workflow surface requires another recertification rather than reusing this statement.

## 9. Explicit non-claims

This certificate does not claim:

- final real-corpus counts, duration, group diversity or source diversity;
- `FIRE_ALARM` / `TIRE_SQUEAL` corpus sufficiency;
- zero cross-format near duplicates in real media;
- final split feasibility against all class floors;
- model winner or thresholds;
- latency/capacity envelope;
- camera compatibility;
- MK1 end-to-end completion.

## 10. Invalidation

`CERT-MK1-DF-TOOLCHAIN-002` becomes `INVALIDATED` when a material change affects the certified code/config/schema/test/workflow surface, including source/acquisition policy, admission/rights, mapping/review, probe/quality, coverage, dedup/grouping, split, freeze/manifests, benchmark handoff or the zero-cost execution contract.