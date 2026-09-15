# MK1 Data Foundry — Gates and Closure Criteria

**Status:** `TOOLCHAIN_RECERTIFICATION_REQUIRED / SONYC_CERTIFIED / CORPUS_CLOSURE_ACTIVE`  
**Toolchain:** `CERT-MK1-DF-TOOLCHAIN-005 = CANDIDATE`  
**SONYC:** `CERT-MK1-DF-SONYC-001 = CERTIFIED`  
**Corpus:** `CERT-MK1-DF-CORPUS-001 = OPEN`  
**Readiness:** `EMP-MK1-CORPUS-READINESS-001 = BLOCKED`  
**Current readiness commit:** `d94eff2958bbe57076610524cbb192d14ec95739`  
**Global invariant:** `ECHO-FREE-TIER-001`

## Gate chain

```text
DF-G0 source registry
  -> DF-G1 provenance/acquisition
  -> DF-G2 rights
  -> DF-G3 exact semantics / governed hard negatives
  -> DF-G4 real-byte integrity + probe + canonical fingerprint
  -> corpus-role boundary
  -> DF-G5 global dedup + acoustic recording-family closure
  -> DF-G6 group-aware split / conflict quarantine
  -> coverage/diversity/hard-negative solidity
  -> DF-G7 freeze #1 -> clean freeze #2 -> reproducibility
  -> EMP-DATASET-001 + EMP-DATA-QUALITY-001
  -> CERT-MK1-DF-CORPUS-001
  -> DF-G8 model-entry
```

No downstream gate compensates for an upstream failure. No paid fallback, label coercion, wrapper double-counting, synthetic source independence, duplicate-family inflation, seed shopping or floor reduction is permitted.

## Certified SONYC node

```text
CERT-MK1-DF-SONYC-001 = CERTIFIED
implementation baseline   ab8c47ba6aabb25390644954a2a06945ca7a81bb
SONYC run                  34922010537
verified shards            19/19 PASS
probe/fingerprint failures 0 / 0
durable evidence           78fc019839f1c9dad1a58a70d439605d887361d7
```

This node is scoped to SONYC materialization/fingerprint closure only.

## DF-G2 / DF-G3 / corpus-role boundary — PASS for admitted ledger

PR #14 quarantined non-release-safe and semantically conflicted rows. PR #15 corrected the boundary so the deliberate pre-grouping marker remains available to the immediately following grouping resolver without masking real blockers.

Current durable result:

```text
input source rows                  1164
retained corpus-role rows          1078
review/non-admissible removed        86
unresolved corpus-facing blockers     0
canonical fingerprints             1078/1078
```

Rejected rows remain durable source evidence. No positive/HN credit was coerced and no license was rewritten.

## DF-G5 — PASS

Current implementation/evidence chain:

```text
PR #15 implementation baseline  4b261bd10d6578a6256fca8ec848ea1055c24b32
Data Foundry CI                  34980804090 PASS
canonical ledger run             34980804004 PASS
canonical ledger evidence        5239447e91915deef30b814c6b172010bd73d2ff
closure evidence run             34980883811 PASS
closure evidence                 b4086d7eb02df67091ac77cd519590abf336b70e
readiness                        d94eff2958bbe57076610524cbb192d14ec95739
```

Global grouping facts:

```text
corpus-facing assets                    1078
fallback assets after grouping             0
global acoustic components                17
members reassigned                         97
content merged/deleted                  false
```

Closure results:

```text
global-dedup-audit.json       PASS / gap_codes=[]
recording-family-audit.json   PASS / gap_codes=[]
missing canonical fingerprints 0
unresolved ledger blockers      0
```

Acoustic fingerprint proximity is used for shared split protection, not as proof that two source objects are identical.

## DF-G6 — PASS via deterministic whole-group quarantine

```text
split-integrity.json = PASS
original split conflicts detected = 3
complete acoustic groups quarantined = 3
quarantined assets = 62
ready candidate assets = 1078
eligible development assets = 1016
```

Conflicting groups are quarantined as complete acoustic components. Source evidence remains retained. Moving individual clips, choosing a favorable seed, or splitting an acoustic component remains forbidden.

## Corpus solidity — frozen

`MK1-CORPUS-SOLIDITY-001` remains unchanged.

Per target:

```text
assets >= 50
groups >= 25
underlying sources >= 2
duration >= 180 s
largest source fraction <= 0.80
train >= 20 assets / 10 groups
validation >= 5 assets / 3 groups
test >= 5 assets / 3 groups
```

Per-target hard negatives require `>=20 assets / >=10 groups / >=2 underlying sources`. Global background/negatives require `>=200 assets / >=50 groups / >=3 underlying sources`.

## Current coverage precheck

```text
FIRE_ALARM      positive 9/50     positive sources 2/2    HN 34/20    HN sources 1/2
GLASS_SHATTER   positive 304/50   positive sources 2/2    HN 401/20   HN sources 1/2
SIREN           positive 173/50   positive sources 3/2    HN 32/20    HN sources 1/2
TIRE_SQUEAL     positive 11/50    positive sources 2/2    HN 0/20     HN sources 0/2
VEHICLE_HORN    positive 245/50   positive sources 3/2    HN 0/20     HN sources 0/2
```

This is only the readiness precheck. `coverage-gate.json` remains FAIL and still enforces duration, group counts, per-split floors, largest-source concentration, quality and rights. Acquisition must include headroom for final dedup/group/split losses rather than merely reaching raw floors.

## Current readiness

At `d94eff2958bbe57076610524cbb192d14ec95739`:

```text
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = 90f2dd006cfbacfe9dc1bdc5cb81c7d9411ccf5322d6ca2dd53f334e76c209e8
```

Current readiness has 16 gap codes. Global dedup, recording-family, split-integrity, canonical fingerprint coverage and ledger blockers are no longer among them. Remaining categories are: corpus certificate absent; coverage not PASS; FIRE_ALARM/TIRE_SQUEAL positive deficits; per-target HN source/asset deficits; Freeze #1/#2 and reproducibility not PASS.

## Highest-value next acquisition

```text
1. FIRE_ALARM: add genuine release-safe positives with margin above the 50-asset/group/duration/split floors.
2. TIRE_SQUEAL: add genuine release-safe positives plus >=20 governed HN assets across >=2 independent source families.
3. FIRE_ALARM / GLASS_SHATTER / SIREN: add a second independent HN source family.
4. VEHICLE_HORN: add >=20 governed HN assets / >=10 groups / >=2 independent sources.
```

More wrappers over the same underlying Freesound family do not create source-family diversity.

## DF-G7 — freeze/reproducibility

Freeze #1/#2 are ineligible while coverage fails. Once coverage is PASS, both freezes must bind exact membership, media hashes, groups, splits, source/rights/mapping policies, dedup and coverage evidence. A second clean process build must reproduce the same semantic identity before reproducibility can pass.

## DF-G8 — model entry

`build_corpus_closure_readiness.py --require-modeling-ready` must remain non-zero until `CERT-MK1-DF-CORPUS-001` is certified, every required closure node is PASS and `gap_codes=[]`.

No Benchmark A/B/C, model training, threshold calibration, replay progression or real-camera progression is authorized before that transition.

## Certificate lineage

```text
CERT-MK1-DF-SPEC-001        CERTIFIED
CERT-MK1-DF-TOOLCHAIN-004   INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005   CANDIDATE
CERT-MK1-DF-SONYC-001       CERTIFIED / scoped
EMP-DATASET-001              OPEN
EMP-DATA-QUALITY-001         OPEN
CERT-MK1-DF-CORPUS-001      OPEN
```

## Product direction

The Foundry is not a side project. It is the evidence foundation for ECHO's acoustic classifier. Once corpus certification closes, active priority must move immediately to Benchmark A/B/C rather than continuing Foundry polishing without a blocker-driven reason.

## Invalidation

Any material change to taxonomy, source/acquisition, rights/mapping/review, probing/fingerprints, grouping/dedup, split/coverage/freeze/handoff semantics, readiness/model-entry guard, SONYC evidence, tests/schemas/workflows, governing documentation or `ECHO-FREE-TIER-001` requires dependency review and selective recertification.