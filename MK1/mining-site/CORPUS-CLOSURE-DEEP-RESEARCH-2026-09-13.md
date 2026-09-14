# MK1 Corpus Foundry Closure — Deep Research Synthesis

**Research date:** 2026-09-13  
**Repository baseline audited:** `main@ffc3d4fb4dfcc277d8abe76022255568939b59f1`  
**Status:** `RESEARCH_COMPLETE / EXECUTION_GUIDANCE_ACTIVE`  
**Normative project promise:** **“Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial”**

## 1. Purpose

This document records the research findings that determine how MK1 Corpus Foundry Closure must proceed. It is evidence/guidance, not a certificate and not a substitute for machine-generated empirical reports.

ECHO must not move to model benchmark A/B/C until the release-safe corpus has passed the complete Foundry gate chain and the final frozen bundle is reproducible, leakage-resistant and bound to exact source/policy/data identities.

## 2. Evidence classes

The following labels are used throughout this document:

- **FACT/EVIDENCE** — directly supported by the repository, publisher documentation or primary tooling documentation.
- **INFERENCE** — engineering conclusion derived from evidence.
- **HYPOTHESIS** — candidate rule that still requires empirical validation.
- **DECISION** — ECHO project rule adopted for execution.
- **TARGET** — required future state, not yet claimed as achieved.

## 3. Primary external evidence consulted

### GitHub Actions

Official GitHub-hosted runner documentation states that standard public Linux runners are finite ephemeral machines and that larger runners are a distinct billable capability.

- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/actions/concepts/billing-and-usage

**DECISION:** `ECHO-FREE-TIER-001` remains stricter than provider limits. ECHO uses standard public Linux runners only, targets a maximum 10 GiB per-job working set, does not use raw datasets as GitHub artifacts, and never solves capacity by enabling billing.

### FSD50K

Official release:

- https://zenodo.org/records/4060432

FSD50K provides 51,197 clips, 108.3 hours and 200 classes, with publisher metadata/ground truth and underlying Freesound identities/licenses.

**INFERENCE:** FSD50K metadata is valuable even when the full multipart audio archive is not materialized. Exact candidate Freesound IDs can be selected from official ground truth and acquired independently under current per-asset rights.

**DECISION:** FSD50K and direct Freesound views of the same underlying sound never count as two physically independent sources.

### SONYC-UST

Official release:

- https://zenodo.org/records/3966543

SONYC-UST is an urban acoustic sensor dataset distributed in bounded publisher bundles.

**DECISION:** process SONYC shard-by-shard, verify publisher bundle evidence, emit compact per-asset hash/probe/label/grouping evidence and delete raw shard bytes before the next shard.

### SINGA:PURA

Official release:

- https://zenodo.org/records/5645825

SINGA:PURA supplies strongly labelled urban audio and can be treated with bounded/selective extraction.

**DECISION:** metadata/annotations first, then only bounded members required by the selected corpus path; no monolithic extraction that breaches the free-tier working-set policy.

### FFmpeg / ffprobe

Primary documentation:

- https://ffmpeg.org/ffprobe.html

**FACT/EVIDENCE:** `ffprobe` can inspect audio stream/container metadata without needing persistent transcoded copies.

**DECISION:** every admitted real-byte asset must have technical audio evidence, including positive duration and valid audio stream information.

### Acoustic fingerprinting / near-duplicate screening

Relevant open-source reference:

- https://github.com/acoustid/chromaprint

**FACT/EVIDENCE:** robust audio identity can be based on acoustic content rather than only file bytes.

**INFERENCE:** ECHO does not need an external AcoustID service or paid API. It only needs a deterministic local near-duplicate screening strategy sufficient to prevent cross-split leakage.

## 4. Current Foundry gate chain

The existing architecture is directionally correct and remains frozen as the gate order:

```text
DF-G0 source registry
  -> DF-G1 release / provenance
  -> DF-G2 rights
  -> DF-G3 semantic mapping / review
  -> DF-G4 content integrity / quality
  -> DF-G5 grouping / dedup
  -> DF-G6 split / holdout
  -> DF-G7 frozen bundle
  -> DF-G8 benchmark handoff
```

**DECISION:** downstream PASS cannot compensate for an upstream FAIL. Any failed ancestor keeps `CERT-MK1-DF-CORPUS-001` open.

## 5. Current solidity floor

`MK1-CORPUS-SOLIDITY-001` remains a defensible **engineering certification floor**, not a claim of model sufficiency.

Per target class:

```text
>= 50 admitted assets
>= 25 independent recording groups
>= 2 independent underlying source datasets
>= 180 s positive clip exposure
train      >= 20 assets / 10 groups
validation >= 5 assets / 3 groups
test       >= 5 assets / 3 groups
largest single source fraction <= 0.80
```

Development negative pool:

```text
>= 200 background / hard-negative assets
>= 50 independent negative groups
>= 3 negative sources
```

Per target hard negatives:

```text
>= 20 assets
>= 10 groups
>= 2 sources
```

**FACT/EVIDENCE:** these values are already represented in the versioned ECHO coverage policy.

**DECISION:** they are minimum engineering gates only. Model sufficiency remains empirical and is decided later by benchmark metrics, not by corpus counts alone.

## 6. Semantic non-negotiables

Frozen MK1 targets remain:

```text
GLASS_SHATTER
SIREN
FIRE_ALARM
VEHICLE_HORN
TIRE_SQUEAL
```

`BACKGROUND_NO_TARGET` remains a training/evaluation state. `UNKNOWN` remains decision-layer abstention.

**DECISION:** broad labels do not automatically become exact positives:

```text
Alarm        != FIRE_ALARM
Squeak       != TIRE_SQUEAL
Car          != VEHICLE_HORN
Glassware    != GLASS_SHATTER
```

Ambiguous candidates require approved asset-level semantic evidence or remain quarantined.

`FIRE_ALARM` and `TIRE_SQUEAL` remain the highest-risk target-data nodes and must be closed with direct defensible evidence rather than semantic widening.

## 7. Canonical asset ledger requirements

Every admitted asset used for corpus certification must carry enough evidence to reconstruct why it is eligible:

```text
asset_id
source_dataset
source_release
source_asset_id
origin_uri
sha256
byte_size
license_id
use_decision
original_labels
echo_labels
mapping_status
label_provenance
duration_seconds
sample_rate_hz
channels
recording_group_id
original_split
echo_split
field_holdout
admission_status
reason_codes
manual review evidence when required
near-duplicate evidence
hard_negative_for when applicable
```

**DECISION:** a metadata row without materialized/verifiable real bytes does not receive release-safe corpus credit.

## 8. Underlying-source independence

A critical diversity rule is now explicit:

```text
same underlying acoustic recording
wrapped by FSD50K
and acquired from Freesound directly

=> one recording family
=> one underlying source family
=> not two independent-source credits
```

**DECISION:** source diversity is about underlying acoustic origin, not metadata wrapper count.

The strongest available grouping identity always wins:

```text
physical event / continuous session
  > original recording
  > source/uploader + occurrence
  > sensor/site/time block
  > clip id only when no stronger relationship exists
```

## 9. Near-duplicate research finding

The current lightweight fingerprint implementation is useful but not sufficient for final corpus certification because it is format-limited and exact-fingerprint based.

Known blind spot:

```text
same acoustic content
  ├─ WAV PCM16 -> fingerprint available
  ├─ MP3/OGG   -> may not produce the same current fingerprint path
  └─ re-encode -> byte SHA changes and exact fingerprint equality can fail
```

**DECISION:** before final corpus certificate, all admitted formats must be canonical-decoded locally into a deterministic mono 16 kHz PCM stream for near-duplicate screening. No decoded copy needs to persist.

Recommended canonical decode:

```text
ffmpeg input
  -> first audio stream
  -> mono
  -> 16 kHz
  -> signed 16-bit PCM stream
  -> deterministic fingerprint/vector
```

**HYPOTHESIS:** a quantized normalized-envelope vector with a proximity rule can be a lightweight MK1 solution, but its threshold must be validated by fixtures rather than chosen by intuition.

Required fixture classes:

```text
expected duplicate:
- original vs re-encoded
- gain-adjusted copy
- mono/stereo conversion
- sample-rate conversion

expected independent:
- different event, same class
- different alarms of same type
- different horns
- different glass breaks
- different tire squeals
```

**TARGET:** all expected transformed duplicates detected and zero known-independent fixture pairs declared duplicates before freezing the near-duplicate policy version.

## 10. Split policy finding

The existing split logic is deterministic and group-aware, but it is not a constrained class-stratified allocator.

**DECISION:** do not fix split shortages by moving clips manually and do not repeatedly change seeds until the numbers look convenient.

Correct behavior:

```text
split_policy.v1 satisfies all floors
    -> keep v1

split_policy.v1 fails a floor
    -> certificate remains OPEN
    -> design/freeze split_policy.v2
    -> deterministic whole-group constrained allocation
    -> rerun all split evidence
```

Any v2 allocator must move complete groups, preserve upstream protected splits when required, and use a stable deterministic tie-break.

## 11. Hard-negative integration finding

The semantic mapping policy for hard negatives exists, but the mapping alone is not empirical evidence.

A hard negative only receives coverage credit after:

```text
real bytes
+ provenance
+ release-safe rights
+ technical probe PASS
+ recording family
+ exact dedup
+ near-dup screen
+ explicit hard_negative_for
```

**TARGET:** add a dedicated bounded hard-negative materialization execution surface that produces machine-readable evidence from the frozen mapping.

## 12. Corpus Closure integration finding

The repository already contains most lower-level Foundry primitives, but certification needs one final integration surface whose only purpose is to decide whether the corpus can be signed.

**TARGET:** a final closure workflow must consume compact durable ledgers/evidence and run, fail-closed:

```text
free-tier preflight
-> schema validation
-> global ledger validation
-> rights validation
-> semantic/review validation
-> hard-negative validation
-> exact dedup
-> near-dup validation
-> recording-family validation
-> group-aware split
-> coverage/diversity gate
-> freeze
-> bundle validation
-> independent second freeze
-> identity comparison
-> certification evidence
```

It must not redownload entire raw corpora merely to certify evidence that is already cryptographically bound and rehydratable.

## 13. Final certification predicate

`CERT-MK1-DF-CORPUS-001` may become `CERTIFIED` only when all of the following are true:

```text
publisher/source evidence               PASS
release-safe rights                     PASS
semantic mapping/reviews                PASS
real-byte integrity                     PASS
audio probe/quality                     PASS
hard-negative coverage                  PASS
exact dedup                              PASS
near-duplicate screening                PASS
recording-family isolation              PASS
split integrity                         PASS
positive coverage                       PASS
background coverage                     PASS
source diversity                        PASS
field holdout isolation                 PASS
bundle hash binding                     PASS
bundle validation                       PASS
reproducibility                         PASS
ECHO-FREE-TIER-001                       PASS
coverage-gate.status                     PASS
coverage-gate.gap_codes                  []
```

If any item fails, correct state is `OPEN`, not a weakened threshold, hidden exception or paid workaround.

## 14. What must not happen yet

Until the corpus certificate closes:

```text
NO final YAMNet vs PANNs/Cnn14 vs ECHO-CNN benchmark claim
NO production threshold tuning
NO model-winner declaration
NO field-performance claim
NO MK1 final certification
```

Synthetic fixtures and model smoke tests remain permitted only as engineering tests and cannot be presented as empirical corpus/model validation.

## 15. Path after corpus closure

Once `CERT-MK1-DF-CORPUS-001` is legitimately certified:

```text
frozen corpus identity
  -> benchmark A/B/C
  -> calibrated model candidate
  -> temporal Event Engine
  -> offline replay
  -> multi-source replay/resource tests
  -> real camera/microphone gate
  -> MK1 end-to-end certification
```

Every stage continues under the global zero-cost boundary and inherits the same fail-closed evidence principle.
