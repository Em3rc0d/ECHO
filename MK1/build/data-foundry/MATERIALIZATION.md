# MK1 Dataset Materialization

**Status:** `ACTIVE_BOUNDED_EXECUTION / CORPUS_CERTIFICATE_OPEN`  
**Global invariant:** `ECHO-FREE-TIER-001`  
**Profile target:** `release_safe`

ECHO does not call a dataset “materialized” merely because a source URL, metadata row or class count exists. Materialization credit requires real bytes to have been observed and bound to durable evidence. Corpus admission additionally requires the complete Data Foundry chain.

## Corpus objective

The frozen MK1 taxonomy is:

```text
GLASS_SHATTER
SIREN
FIRE_ALARM
VEHICLE_HORN
TIRE_SQUEAL
```

The materialization plan is versioned in:

```text
configs/data_foundry/materialization_plan.v1.json
```

Exact-gap candidate discovery lives in:

```text
configs/data_foundry/gap_source_candidates.v1.json
```

The closure runbook is:

```text
MK1/build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md
```

## Source families

```text
Publisher corpora
  SONYC-UST v2.3
  FSD50K v1.0 metadata / defensible per-asset path
  SINGA:PURA v1.0a bounded path
  ESC-50 research-only pinned path
  UrbanSound8K research-only/manual-free-access path

Gap-closing sources
  Freesound exact-category/current per-asset candidates
  BigSoundBank CC0 exact candidates
  Wikimedia-compatible public candidates when policy-compatible
  other individually licensed public assets only after provenance review

Augmentation/reference only
  synthetic alarm material where explicitly marked augmentation
  AudioSet ontology/annotations

Field
  ECHO Field Dataset — untouched holdout after authorization
```

No synthetic dataset receives independent-real-source credit. AudioSet raw media is not auto-ingested. Broad labels such as generic alarm, generic screeching or generic friction sounds cannot silently close an exact target gap.

## Zero-cost execution boundary

This document inherits `governance/FREE-TIER-BOUNDARY.md`.

The old monolithic assumption “download all corpora to a large persistent node” is **not** the ECHO default path. ECHO must remain under the project working-set ceiling and may not introduce a paid/self-hosted capacity dependency merely to close corpus execution.

Canonical execution pattern:

```text
bounded shard / asset batch
        ↓
download within standard public runner boundary
        ↓
verify publisher/source evidence
        ↓
probe + SHA-256 + semantic/rights evidence
        ↓
emit compact durable manifest/report/checkpoint
        ↓
delete raw/extracted bytes
        ↓
next shard / asset batch
```

No workflow may require a working set above the project ceiling defined by `ECHO-FREE-TIER-001`. Raw corpora are not GitHub artifacts or Git history.

### Current source execution posture

- `SONYC-UST`: shard-by-shard execution is the canonical path.
- `SINGA:PURA`: bounded/selective extraction only.
- `FSD50K`: full multipart audio materialization is not a mandatory release-safe dependency. Official metadata/ground truth may identify exact underlying Freesound assets, which are then handled under current per-asset rights/provenance.
- `ESC-50`: research-only; only pinned/free execution that fits the boundary.
- `UrbanSound8K`: research-only/manual free-access path; never purchase access.
- public gap sources: incremental per-asset execution is preferred.
- `ECHO Field Dataset`: external authorized capture; excluded from development coverage.

If a source cannot be executed inside the boundary without weakening quality, the source/node remains `OPEN` or is replaced by another defensible zero-cost source. Payment is not a fallback.

## Durable materialization evidence

Repository evidence may include:

```text
publisher/source snapshot
source asset ID / origin URI
publisher checksum when available
local media SHA-256 observed during execution
byte size
audio probe metadata
license/use evidence
semantic label provenance
recording-family/group evidence
materialization status/reason codes
```

The raw audio may be transient. The evidence must be sufficient to reconstruct exactly what bytes/source identity received or did not receive corpus credit.

## Corpus admission stop line

A source asset is not corpus-ready until:

```text
publisher/source identity
        ↓
real bytes observed
        ↓
publisher checksum where applicable
        ↓
SHA-256 per local representation
        ↓
audio probe
        ↓
license/use decision
        ↓
exact semantic mapping/manual review where required
        ↓
recording/uploader/site/family grouping
        ↓
exact + canonical near-duplicate audit
        ↓
group-aware split
        ↓
coverage/diversity/hard-negative gate
```

Materialization success is therefore necessary but never sufficient for corpus certification.

## FIRE_ALARM and TIRE_SQUEAL

These classes are no longer “unknown source” research problems. Public candidate pools have been identified and real public assets have begun to be materialized. They remain **rights + semantic + diversity + grouping + dedup + split + coverage** closure problems.

Historical FreesoundDataset explorer counts are discovery evidence only. Additional public candidates from independently governed sources can improve source diversity only when the underlying recording is genuinely independent.

Candidate or downloaded counts are never admitted counts.

## Full closure predicate

The accepted terminal condition for a release-safe corpus remains:

```text
rights / semantics / technical quality     PASS
hard-negative requirements                 PASS
exact duplicate leakage                    0
near-duplicate leakage                     0
recording-family cross-split leakage       0
field holdout contamination                0
coverage-gate.json.status                  PASS
coverage-gate.json.gap_codes               []
bundle validation                          PASS
second clean freeze reproducibility        PASS
ECHO-FREE-TIER-001                          PASS
CERT-MK1-DF-CORPUS-001                     CERTIFIED
```

Anything else remains open.

## Operational next step

`EXEC-DATA-001` now means **bounded corpus closure execution**, not monolithic dataset residency:

```text
consume existing materialization evidence
+ continue bounded zero-cost acquisition where gaps remain
+ build canonical global asset ledger
+ close per-asset rights/semantics
+ materialize hard negatives
+ harden cross-format near-duplicate screening
+ run global grouping/dedup/split/coverage
+ freeze twice and compare identities
+ certify only if every required gate passes
```

No model benchmark may bypass `CERT-MK1-DF-CORPUS-001`.