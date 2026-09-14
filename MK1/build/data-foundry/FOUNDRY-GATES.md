# MK1 Data Foundry — Gates and Closure Criteria

**Status:** `TOOLCHAIN_CERTIFIED / REAL_CORPUS_CLOSURE_ACTIVE`  
**Current toolchain certificate:** `CERT-MK1-DF-TOOLCHAIN-003`  
**Current corpus readiness:** `EMP-MK1-CORPUS-READINESS-001 = BLOCKED`  
**Global invariant:** `ECHO-FREE-TIER-001`

## Gate chain

```text
DF-G0 source registry
  -> DF-G1 release/provenance
  -> DF-G2 rights
  -> DF-G3 semantics/review
  -> DF-G4 real-byte integrity/quality
  -> DF-G5 exact + near-duplicate/group audit
  -> DF-G6 group-aware split/holdout audit
  -> coverage/diversity/hard-negative solidity
  -> DF-G7 frozen bundle
  -> second clean freeze/reproducibility
  -> corpus certificate
  -> DF-G8 benchmark handoff/model-entry gate
```

A downstream gate cannot compensate for an upstream failure. All execution inherits `ECHO-FREE-TIER-001`; paid fallbacks and lowered quality floors are forbidden.

## DF-G0 — Source identity

Every selected source requires a stable source ID/release/evidence URL, license model and intended role. Dataset wrapper identity is not automatically an independent acoustic source. If FSD50K and direct Freesound records resolve to the same underlying recording, they share source/recording-family credit.

## DF-G1 — Provenance/acquisition

Real coverage requires observed media bytes or a source-specific path that yields them during bounded materialization. Metadata-only rows remain evidence but do not create release-safe positive/hard-negative credit. Upstream checksums are retained when publishers expose them; local asset identity uses SHA-256.

## DF-G2 — Rights

Every admitted `release_safe` asset needs a compatible rights decision. `UNKNOWN`, `REVIEW_REQUIRED`, incompatible/non-commercial-only rights or unresolved redistribution/use terms fail closed. Rights cannot be overridden by a strong label.

## DF-G3 — Semantics

Positive admission requires exact/narrow evidence or explicit asset-level review. Frozen stop-lines:

```text
Alarm      != FIRE_ALARM
Squeak     != TIRE_SQUEAL
Car        != VEHICLE_HORN
Glassware  != GLASS_SHATTER
```

Hard-negative labels never become positives by convenience.

## DF-G4 — Technical evidence

Every admitted row must have:

```text
real bytes observed
positive byte size
SHA-256
valid audio probe
positive duration
source provenance
label provenance
canonical fingerprint where required
```

The current canonical ledger still reports 599 assets without canonical fingerprints and additional missing asset-level probe/byte-size evidence; therefore final closure is not eligible yet.

## DF-G5 — Global duplicate/group audit

Final certification requires canonical mono 16 kHz signed-16-bit PCM fingerprinting sufficient for transcode-aware comparisons, validated transformed-copy/known-independent fixtures, and global grouping using the strongest available relationship:

```text
same physical event/session
> same original recording
> source/uploader occurrence family
> sensor/site/time block
> clip ID fallback
```

Required output: `global-dedup-audit.json` and `recording-family-audit.json`, both PASS, with no protected-split leakage.

## DF-G6 — Split integrity

Group-aware splitting must produce:

```text
group overlap = 0
exact duplicate overlap = 0
near-duplicate overlap = 0
field holdout overlap = 0
```

and satisfy all class/split floors. Seed shopping/manual clip movement is forbidden. If policy v1 cannot satisfy constraints, a new deterministic whole-group allocator must be versioned and re-audited.

Required output: `split-integrity.json = PASS`.

## Corpus solidity

`MK1-CORPUS-SOLIDITY-001` remains the engineering floor.

Per target:

```text
>=50 assets
>=25 independent groups
>=2 underlying source families
>=180 s
largest source <=80%
train >=20 assets / 10 groups
validation >=5 / 3
test >=5 / 3
```

Global negatives: >=200 assets / >=50 groups / >=3 sources. Per-target hard negatives: >=20 assets / >=10 groups / >=2 sources.

Field holdout, synthetic augmentation, broad labels and repeated segments cannot manufacture independent coverage.

Current pre-final canonical counts identify critical gaps:

```text
FIRE_ALARM positives   5 / 50
TIRE_SQUEAL positives  5 / 50
TIRE_SQUEAL positive source families 1 / 2
VEHICLE_HORN hard negatives 0 / 20, sources 0 / 2
TIRE_SQUEAL hard negatives  0 / 20, sources 0 / 2
FIRE_ALARM hard-negative sources     1 / 2
GLASS_SHATTER hard-negative sources  1 / 2
SIREN hard-negative sources          1 / 2
```

These floors are never lowered to obtain certification.

Required output: `coverage-gate.json` with `status=PASS` and `gap_codes=[]`.

## DF-G7 — Freeze and reproducibility

Freeze #1 must bind asset membership, SHA-256, recording families, splits, rights/mapping policy, source policy, coverage and dedup/quarantine evidence. It is then validated.

A second clean freeze over unchanged inputs must reproduce semantic identity:

```text
same assets
same hashes
same recording families
same splits
same duplicate decisions
same coverage/gaps
```

Required outputs:

```text
corpus-freeze-1.validation.json = PASS
corpus-freeze-2.validation.json = PASS
corpus-reproducibility.json = PASS
```

## Readiness and certificate review

`EMP-MK1-CORPUS-READINESS-001` is generated deterministically from the canonical ledger, coverage policy and named closure evidence. It distinguishes:

- `eligible_for_certificate_review`: all prerequisite closure evidence passes;
- `modeling_allowed`: certificate review has also promoted `CERT-MK1-DF-CORPUS-001` to `CERTIFIED` and no gap remains.

Current state is `BLOCKED / modeling_allowed=false`.

## DF-G8 — Benchmark handoff

Manual directory selection is forbidden. Benchmark configuration must consume an exact validated Foundry bundle identity.

The reusable `MK1 Model Entry Gate` runs:

```text
python scripts/data_foundry/build_corpus_closure_readiness.py --require-modeling-ready
```

and fails non-zero until the certified corpus predicate is satisfied. Future model/benchmark/train workflows are checked for bypass wiring.

## Certificate lineage

```text
CERT-MK1-DF-SPEC-001       CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001  historical
CERT-MK1-DF-TOOLCHAIN-002  historical / superseded
CERT-MK1-DF-TOOLCHAIN-003  CERTIFIED / current
EMP-DATASET-001             OPEN
EMP-DATA-QUALITY-001        OPEN
CERT-MK1-DF-CORPUS-001     OPEN
```

`CERT-MK1-DF-TOOLCHAIN-003` is tied to implementation baseline `dc225803b5c066b365779fdc2b4b2f0984bb7e19`, Data Foundry CI run `34904125873`, Corpus Closure Readiness run `34904125899`, and Free-Tier run `34904125820`. Durable readiness evidence is persisted at commit `aac662b770669bf633dd58a582514abcb39c30a1`.

The toolchain certificate proves the fail-closed machinery works; it does not certify the corpus.

## Invalidation

Changes to taxonomy, source/acquisition semantics, rights/mapping/review, technical probing/fingerprints, grouping/dedup, split/coverage/freeze/handoff logic, readiness/model-entry guard, certified tests/schemas/workflows, or `ECHO-FREE-TIER-001` invalidate dependent evidence until rerun/review.
