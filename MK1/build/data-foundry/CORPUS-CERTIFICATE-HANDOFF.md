# MK1 Corpus Certificate Handoff

**Authority:** `CERT-MK1-DF-HANDOFF-001`  
**Status:** `CERTIFIED`  
**Scope:** transition from fully closed corpus evidence to `CERT-MK1-DF-CORPUS-001` and model-entry authorization  
**Global invariant:** `ECHO-FREE-TIER-001`

## Purpose

This contract defines the only authorized automatic transition from Data Foundry closure into Benchmark A/B/C. It is intentionally stable and is not a rolling snapshot of current corpus counts.

## Preconditions

A corpus certificate may be emitted only when a freshly rebuilt pre-certificate readiness artifact satisfies all of the following:

```text
schema_version = echo.corpus-closure-readiness.v2
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = true
modeling_allowed = false
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
gap_codes = [CORPUS_CERTIFICATE_NOT_CERTIFIED]
```

Every required closure evidence node must be present, PASS, have `gap_codes=[]` where applicable, and be bound by `evidence_identity_material`. The canonical semantic ledger hash and coverage-policy hash must agree with that identity.

## Stable ancestors

The certificate binds these stable authorities by SHA-256:

```text
CERT-MK1-DF-TOOLCHAIN-005
CERT-MK1-DF-HANDOFF-001
ECHO-FREE-TIER-001
```

A rolling documentation-current certificate is deliberately not a runtime ancestor. Documentation governance may advance after corpus certification without invalidating an otherwise unchanged corpus certificate.

## Issuance

The canonical corpus orchestrator is the only durable writer. It must:

1. rebuild ledger, grouping, dedup/family/split, coverage, freeze #1/#2 and reproducibility from one exact baseline;
2. build pre-certificate readiness while ignoring any existing corpus certificate;
3. emit or reuse `CERT-MK1-DF-CORPUS-001` only if the preconditions above are exact;
4. rebuild final readiness with the certificate applied;
5. require final `modeling_allowed=true`, `status=READY`, `gap_codes=[]` and `next_authorized_stage=BENCHMARK_A_B_C` when a certificate is issued;
6. repeat the full process and compare durable outputs for determinism;
7. refuse persistence if `main` moved;
8. persist corpus evidence, certificate and final readiness atomically.

When the preconditions are not satisfied, certificate issuance is a successful no-op and readiness remains fail-closed.

## Certificate validity

A certificate is valid only when all of these remain true:

- `certificate_sha256` matches its canonical JSON payload;
- `semantic_evidence_identity_sha256` equals current readiness identity;
- toolchain, handoff and free-tier ancestor hashes equal the current certified files;
- empirical outputs `EMP-DATASET-001` and `EMP-DATA-QUALITY-001` are PASS;
- every certificate criterion is PASS.

A provenance-only rebuild may change execution commit or summary-file bytes without invalidating the certificate when the semantic evidence identity and stable ancestors are unchanged.

## Invalidation

The certificate must fail closed if the semantic corpus/readiness identity, coverage policy, closure evidence, rights/mapping/grouping/split/freeze semantics, Toolchain-005, this handoff authority or `ECHO-FREE-TIER-001` changes.

## Non-claims

This contract does not certify a model, threshold, field performance, replay behavior or camera integration. It only authorizes the transition into Benchmark A/B/C after corpus closure is actually certified.
