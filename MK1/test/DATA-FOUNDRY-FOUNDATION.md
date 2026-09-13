# MK1 Data Foundry Foundation — Test Evidence

**Status:** `PASS / FOUNDATION_ONLY`

## 1. Scope

This record certifies the **Foundry foundation implementation**, not the final ECHO corpus or ML benchmark. It covers typed contracts, source registry validation, license policy, semantic mapping, deterministic split primitives, canonical manifests, source metadata adapters, admission behavior and JSON policy/schema syntax.

## 2. Build under test

- Foundry foundation commit: `586a6320ac45522be1cf475a525ae4713b88e8e8`
- CI workflow commit: `1ad8a4a8635c973722ae69646c8fb6005abcee42`
- Workflow: `MK1 Data Foundry CI`
- GitHub Actions run: `34741450390`
- Runner image observed: Ubuntu 24.04 family

## 3. Matrix

| Runtime | Job | Result |
|---|---|---|
| Python 3.10 | `foundry-foundation (3.10)` | PASS |
| Python 3.11 | `foundry-foundation (3.11)` | PASS |
| Python 3.12 | `foundry-foundation (3.12)` | PASS |

All three jobs completed successfully.

## 4. Executed gates

Each matrix job executed:

```text
python -m compileall -q src tests
PYTHONPATH=src python -m echo.data_foundry.cli validate-source-registry configs/data_foundry/source_registry.v1.json
python -m json.tool ... (all Foundry JSON policies/schemas)
PYTHONPATH=src python -m unittest discover -s tests -v
```

The registry command returned `status=PASS` with seven registered source families.

## 5. Unit evidence

Python 3.11 job executed **23 tests** with `OK`. Test groups cover:

- FSD50K, SONYC-UST, SINGA:PURA, ESC-50 and UrbanSound8K metadata adapters;
- FSD50K MID/vocabulary parsing so class display names containing commas are not naively split;
- permissive/non-commercial/ShareAlike/unknown license-policy behavior;
- exact vs broader/ambiguous semantic label mapping;
- quarantine of broad positive mappings pending review;
- rejection/quarantine behavior for incompatible release-safe rights;
- deterministic group-aware split assignment;
- exact-content cross-split leakage detection;
- input-order-independent canonical manifest hashing;
- dataset manifest count/source derivation.

## 6. What this PASS means

`FACT/EVIDENCE`: the current foundation compiles and passes its unit/structure checks on Python 3.10–3.12 in GitHub-hosted Linux CI.

`DECISION`: this is sufficient evidence to certify `CERT-MK1-DF-SPEC-001` for the Foundry **specification/core foundation**.

It does **not** certify:

- that upstream source archives have been fully acquired locally;
- exact admitted asset counts/durations;
- audio decoding/resampling correctness;
- near-duplicate fingerprint coverage;
- final train/validation/test composition;
- target data sufficiency;
- model quality or field performance.

Those remain empirical Foundry/corpus gates.

## 7. Known warnings

The first CI run emitted a GitHub-hosted warning that the action versions used by the workflow are being forced onto a newer Node runtime. It did not affect job success or Python test results. Action-version maintenance should be handled as normal CI dependency maintenance rather than hidden.

## 8. Invalidation

This evidence must be re-run when Foundry code, policy JSON, schema JSON, source adapters or split/manifest semantics change materially. New data alone does not invalidate the foundation test, but it requires corpus-level gates and reports.