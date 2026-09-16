# Documentation Audit — Corpus Pipeline 014

**Certificate:** `CERT-DOC-014`  
**Status:** `CERTIFIED`  
**Date:** `2026-09-16`  
**Scope:** MK1 corpus evidence pipeline, semantic corpus identity, execution provenance and model-entry stop line  
**Global ancestor:** `ECHO-FREE-TIER-001`

## 1. Decision

DOC-014 supersedes DOC-013 as the current documentation certificate.

The project promise remains unchanged:

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

The corpus pipeline is now governed by an atomic durable cascade. One authoritative writer builds canonical ledger → grouping → dedup/family/split → coverage → freeze #1/#2 → reproducibility → readiness against one resolved baseline and persists the evidence set together. Standalone closure/readiness workflows are read-only diagnostics.

## 2. Semantic identity versus execution provenance

DOC-013 incorrectly froze `baseline_commit` as if it were corpus content. DOC-014 closes that ambiguity.

```text
semantic corpus identity
  = canonical ledger semantic ledger_sha256
  + coverage policy identity
  + closure evidence identities

execution provenance
  = exact commit used to perform the deterministic rebuild
  + byte hash of the generated ledger summary
```

Execution provenance is required and audited, but a new build commit is not itself a new acoustic corpus. A provenance-only rebuild may change `baseline_commit` or summary-file bytes while the canonical semantic ledger remains unchanged.

The current canonical semantic ledger identity is:

```text
cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1
```

The material ledger identity used by closure/coverage is:

```text
93be3dceee44df0dfc51ab38c078f1e1e6587ba91e4fbbc53c3b65065e58bfa8
```

Readiness v2 binds semantic corpus identity, policy and closure evidence. The current projected semantic readiness identity is:

```text
4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
```

## 3. Atomic pipeline contract

The durable MK1 corpus path is:

```text
successful governed source materialization
  ↓
MK1 Canonical Corpus Ledger / atomic orchestrator
  ↓
canonical ledger
  ↓
global recording grouping
  ↓
global dedup + recording-family + split integrity
  ↓
coverage
  ↓
freeze #1 → freeze #2 → reproducibility
  ↓
EMP-MK1-CORPUS-READINESS-001
  ↓
one atomic durable evidence commit
```

The orchestrator resolves one `main` baseline, records it, repeats the complete cascade for byte-level determinism, and refuses persistence if `main` moves before the evidence commit. Repository-token push recursion is not used as a dependency between durable stages.

The standalone closure and readiness workflows are diagnostic-only, exact-SHA, `contents: read`, and cannot persist evidence.

## 4. Current structural truth

```text
canonical rows                         1141
canonical fingerprints                1141 / 1141
ledger blockers                       0
global grouping                       PASS
global dedup                          PASS
recording-family audit                PASS
split integrity                       PASS
quarantined assets                    0
candidate near-duplicate relations    855
confirmed relations                   2
confirmed cross-group conflicts       0
```

The broad `0.02` distance remains screening only. Confirmed non-exact grouping requires distance `<=0.002` plus decoded-sample-count relative delta `<=0.01`. Review-only screening edges never union transitive components.

## 5. Current empirical coverage truth

Coverage remains `FAIL` with exactly 16 empirical gaps and no structural gap.

```text
BACKGROUND       428 assets / 385 groups / 4 sources       PASS
FIRE_ALARM        19 assets / 16 groups / 3 sources         OPEN
GLASS_SHATTER    303 assets / 287 groups / 4 sources        OPEN concentration
SIREN            169 assets / 169 groups                    PASS
TIRE_SQUEAL       14 assets / 10 groups / 2 sources         OPEN
VEHICLE_HORN     235 assets / 235 groups                    PASS
```

Current mathematical lower bounds remain:

```text
FIRE_ALARM   +31 assets / +9 groups
TIRE_SQUEAL  +36 assets / +15 groups
GLASS        +47 surviving non-Freesound positives
             if Freesound remains 280 assets
```

These lower bounds do not authorize manual split placement, source-family inflation, synthetic substitution, license relaxation or quality-floor changes.

## 6. Readiness and release law

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
CERT-MK1-DF-CORPUS-001 = OPEN
modeling_allowed = false
Benchmark A/B/C = LOCKED
```

Freeze #1 and freeze #2 remain blocked only by upstream coverage. Reproducibility remains blocked only because freeze is not eligible.

The release law remains:

```text
NO CERT-MK1-DF-CORPUS-001
=
NO Benchmark A/B/C
NO YAMNet/PANNs/CNN model work
NO EMP-MODEL-001
NO threshold calibration
NO replay progression
NO real camera progression
```

## 7. Certificate lineage

```text
CERT-DOC-001..013              INVALIDATED / historical
CERT-DOC-014                   CERTIFIED / current
CERT-MK1-DF-TOOLCHAIN-004      INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005      CANDIDATE
CERT-MK1-DF-SONYC-001          CERTIFIED / scoped
CERT-MK1-DF-CORPUS-001         OPEN
```

TOOLCHAIN-005 remains a candidate until the active closure/certificate implementation is stabilized and recertified. DOC-014 does not manufacture corpus certification.

## 8. Automated enforcement

`scripts/check_documentation_governance.py` now fails closed on drift of:

- immutable ECHO promise or `ECHO-FREE-TIER-001`;
- documentation/certificate lineage;
- SONYC scoped certificate;
- semantic canonical-ledger identity and corpus counts;
- screen → confirm → group semantics;
- dedup/family/split closure and zero quarantine;
- exact coverage/readiness gaps and quality stop lines;
- readiness v2 semantic identity material;
- mismatch between ledger execution provenance and readiness provenance;
- corpus-certificate/model-entry stop line;
- Markdown inventory and merge-conflict markers.

The documentation workflow recomputes readiness v2 locally before auditing. This projection is read-only and earns no corpus or certificate credit.

## 9. Invalidation

DOC-014 becomes stale if semantic corpus identity, policy, closure evidence, rights/semantics/grouping/split/coverage/freeze logic, readiness schema/identity contract, certificate state, model-entry wiring, immutable promise, free-tier boundary or audited documentation changes.

A provenance-only baseline change does not invalidate DOC-014 when semantic corpus identity and all governed evidence remain identical; provenance must still be valid and internally consistent.
