# MK1 Corpus Foundry Closure Plan

**Status:** `ACTIVE_EXECUTION_PLAN`  
**Certificate target:** `CERT-MK1-DF-CORPUS-001`  
**Profile:** `release_safe`  
**Global execution invariant:** `ECHO-FREE-TIER-001`

## 1. Goal

Close every internal data node required for an auditable, leakage-resistant, reproducible MK1 corpus before any authoritative model benchmark begins.

This plan does not reopen the frozen MK1 taxonomy, system promise or established Foundry architecture. It integrates the existing machinery into a final certifiable execution chain.

## 2. Closure DAG

```text
FREE-TIER PREFLIGHT
        |
        v
DF-G0 SOURCE REGISTRY
        |
        v
DF-G1 PUBLISHER RELEASE / PROVENANCE
        |
        +--------------------+---------------------+
        |                    |                     |
        v                    v                     v
 SONYC SHARDS        SINGA:PURA BOUNDED     FSD50K METADATA
        |                    |                     |
        |                    |                     v
        |                    |             EXACT FREESOUND IDS
        |                    |                     |
        +--------------------+----------+----------+
                                      |
                                      v
                              PUBLIC / FREESOUND
                              TARGETED ACQUISITION
                                      |
                                      v
                              CANONICAL ASSET LEDGER
                                      |
                                      v
DF-G2 RIGHTS --------------------------+
                                      |
                                      v
DF-G3 SEMANTIC MAPPING / REVIEWS
                                      |
                                      v
                         HARD-NEGATIVE MATERIALIZATION
                                      |
                                      v
DF-G4 HASH / PROBE / QUALITY ----------+
                                      |
                                      v
DF-G5 EXACT DEDUP + NEAR-DUP + GROUPING
                                      |
                                      v
DF-G6 GROUP-AWARE SPLIT / HOLDOUT
                                      |
                                      v
                         COVERAGE + DIVERSITY GATE
                               |              |
                            FAIL              PASS
                               |              |
                               v              v
                     TARGETED REACQUIRE   DF-G7 FREEZE
                               |              |
                               +------> rerun |
                                              v
                                     VALIDATE BUNDLE
                                              |
                                              v
                                      SECOND CLEAN FREEZE
                                              |
                                              v
                                     IDENTITY COMPARISON
                                              |
                                              v
DF-G8 BENCHMARK HANDOFF ---------------------+
                                              |
                                              v
                              CERT-MK1-DF-CORPUS-001
```

## 3. Global invariant

No step may require:

```text
paid infrastructure
paid APIs
paid dataset access
paid storage
paid GPU
larger/billable GitHub runner
automatic overage
working set > ECHO project ceiling
raw corpus stored as GitHub artifact
```

If a node cannot close inside the zero-cost execution boundary, the node remains `OPEN` or `EXTERNAL_GATE_OPEN`.

## 4. Gate contracts

### DF-G0 — Source registry

PASS only when all selected sources have stable IDs, releases, canonical publisher evidence, intended corpus role and declared coverage limitations.

FAIL examples:

- unpinned source release;
- source used outside declared role;
- duplicate logical wrappers treated as independent underlying sources.

### DF-G1 — Provenance / release

PASS only when publisher metadata/checksums or equivalent source evidence bind acquired material to the declared release/asset.

FAIL examples:

- publisher checksum mismatch;
- wrong release or filename/member;
- asset page/source identity cannot be reconciled.

### DF-G2 — Rights

PASS only when every admitted `release_safe` asset has a current compatible rights decision.

Fail closed on:

```text
unknown license
research-only license/profile
review-required rights with no closed decision
rights evidence mismatch
```

### DF-G3 — Semantic mapping / review

PASS only when positive labels are exact/narrower-approved or closed by versioned asset-level review.

Forbidden shortcuts:

```text
Alarm -> FIRE_ALARM
Squeak -> TIRE_SQUEAL
Car -> VEHICLE_HORN
Glassware -> GLASS_SHATTER
```

Hard negatives must stay negatives and carry explicit `hard_negative_for` provenance.

### DF-G4 — Content integrity / technical quality

PASS requires, per admitted asset:

```text
real bytes observed
SHA-256
positive byte size
valid audio stream
positive duration
sample rate evidence
channel evidence
source/label provenance
```

Corrupt/missing/unprobeable assets are quarantined and receive no coverage credit.

### DF-G5 — Grouping / dedup

PASS requires:

```text
exact duplicate leakage = 0
near-duplicate leakage = 0
recording-family cross-split leakage = 0
contradictory-label identical-byte conflicts = 0 unresolved
```

Grouping identity must follow the strongest known underlying acoustic relationship, not merely dataset filename.

FSD50K and direct Freesound representations of the same source sound belong to the same underlying family and cannot generate duplicate source-diversity credit.

### DF-G6 — Splits / field holdout

PASS requires whole-group assignment and no protected-boundary overlap.

Current `split_policy.v1` remains authoritative if it satisfies all class/split floors.

If it fails, do not move clips manually and do not seed-shop. A versioned deterministic group-level constrained `split_policy.v2` must be designed and the full split evidence rerun.

Field holdout remains excluded from development coverage.

### Coverage / diversity gate

Current engineering floor remains:

```text
PER TARGET
assets >= 50
groups >= 25
underlying sources >= 2
duration >= 180 s
largest source fraction <= 0.80

TRAIN
assets >= 20
groups >= 10

VALIDATION
assets >= 5
groups >= 3

TEST
assets >= 5
groups >= 3

GLOBAL BACKGROUND / HARD NEGATIVE
assets >= 200
groups >= 50
sources >= 3

PER TARGET HARD NEGATIVE
assets >= 20
groups >= 10
sources >= 2
```

These are an engineering certification floor only. They do not guarantee F1, recall or deployment sufficiency.

### DF-G7 — Frozen bundle

PASS requires mutually consistent:

```text
asset-manifest.jsonl
split-manifest.json
dataset-manifest.json
coverage-report.json
coverage-gate.json
dedup-report.json
quarantine-report.json
```

The dataset manifest must bind relevant policy/config/source/data identities by digest.

### Reproducibility sub-gate

Before corpus certification, run a second clean freeze from the same admitted ledger and policy set.

Required invariants:

```text
same admitted asset membership
same asset SHA-256 identities
same group assignments
same split membership
same dedup decisions
same coverage decision
gap_codes unchanged
```

Volatile timestamps may differ only if explicitly excluded from corpus identity.

### DF-G8 — Benchmark handoff

PASS only when benchmark configuration reads train/validation/test from the exact validated frozen bundle.

Manual directory enumeration or ad-hoc file selection is a FAIL.

## 5. Near-duplicate closure requirement

The current lightweight near-duplicate logic has a format/transcode blind spot and must be hardened before final corpus certificate.

Required strategy:

```text
input audio
  -> local ffmpeg canonical decode
  -> mono
  -> 16 kHz
  -> signed 16-bit PCM stream
  -> deterministic fingerprint/vector
  -> exact/proximity comparison
```

No canonical WAV needs to be persisted.

The final similarity threshold is not frozen by this document. It must be validated using deterministic positive/negative fixtures.

PASS for the chosen policy version requires:

```text
all known transformed-copy fixtures detected
AND
zero known-independent fixtures declared duplicates
```

## 6. Hard-negative closure requirement

The frozen mapping policy is an input, not proof of materialized negative coverage.

A hard negative receives corpus credit only after:

```text
real bytes
+ source provenance
+ release-safe rights
+ technical probe
+ recording family
+ exact dedup
+ near-duplicate screening
+ hard_negative_for
```

A dedicated bounded materialization/reporting execution surface must produce:

```text
hard-negative-assets.jsonl
hard-negative-materialization-report.json
SHA256SUMS.txt or equivalent content digest evidence
```

Raw media must not be retained as a GitHub dataset artifact.

## 7. Canonical durable evidence packet

The certificate package should converge on:

```text
CERT-MK1-DF-CORPUS-001/
├── baseline.json
├── source-evidence/
├── materialization/
├── semantic/
├── corpus/
│   ├── asset-manifest.jsonl
│   ├── split-manifest.json
│   ├── dataset-manifest.json
│   ├── coverage-report.json
│   ├── coverage-gate.json
│   ├── dedup-report.json
│   └── quarantine-report.json
├── reproducibility/
│   ├── first-freeze-hashes.txt
│   ├── second-freeze-hashes.txt
│   └── validation-result.json
└── certification.json
```

`certification.json` must not be emitted as `CERTIFIED` unless every required gate is backed by actual evidence.

## 8. Final certificate predicate

Conceptually:

```json
{
  "certificate_id": "CERT-MK1-DF-CORPUS-001",
  "profile": "release_safe",
  "status": "CERTIFIED",
  "coverage_status": "PASS",
  "gap_codes": [],
  "exact_duplicate_cross_split": 0,
  "near_duplicate_cross_split": 0,
  "recording_family_cross_split": 0,
  "field_holdout_used_for_dev_coverage": false,
  "free_tier_boundary": "PASS",
  "bundle_validation": "PASS",
  "reproducibility": "PASS"
}
```

Any different empirical state must remain `OPEN`, `CANDIDATE`, `INVALIDATED` or `EXTERNAL_GATE_OPEN` as appropriate.

## 9. Immediate execution order

```text
1. free-tier / CI / source-cert preflight on exact HEAD
2. consume/refresh publisher materialization evidence
3. build one canonical global asset ledger
4. close per-asset rights + semantic review
5. materialize and admit hard negatives
6. canonical near-duplicate hardening + fixture validation
7. global exact/near dedup + recording-family audit
8. group-aware split
9. coverage/diversity gate
10. targeted free reacquisition for remaining gap_codes
11. freeze + validate
12. second clean freeze + compare
13. emit corpus certificate only if all PASS
14. unlock benchmark A/B/C
```

## 10. What remains blocked until corpus closure

Authoritative execution/claims for:

```text
YAMNet vs PANNs/Cnn14 vs ECHO-CNN winner
production class thresholds
final calibration
final model quality claims
Event Engine tuning against final classifier
MK1 end-to-end certification
```

Engineering smoke tests remain allowed but must be labelled as such.

## 11. Post-corpus path

```text
CERT-MK1-DF-CORPUS-001
        ↓
benchmark A/B/C
        ↓
selected/calibrated model candidate
        ↓
temporal Event Engine
        ↓
offline replay
        ↓
multi-source replay + CPU/RAM/latency tests
        ↓
real capture device gate
        ↓
MK1 end-to-end evidence
        ↓
MK1 certification decision
```

Every node inherits `ECHO-FREE-TIER-001` unless a future explicit governance change supersedes that global invariant. No implicit paid fallback is allowed.
