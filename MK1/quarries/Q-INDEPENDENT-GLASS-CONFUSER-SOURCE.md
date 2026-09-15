# Quarry — independent GLASS_SHATTER / confuser source

**Status:** `ACQUISITION_IMPLEMENTED / REAL-BYTE EVIDENCE PENDING`  
**Target gate:** `MK1-CORPUS-SOLIDITY-001`  
**Primary blockers addressed:** `GLASS_SHATTER_SOURCE_CONCENTRATION_TOO_HIGH`, `GLASS_SHATTER_HARD_NEGATIVE_SOURCES_BELOW_MIN`, partial `BACKGROUND_SOURCES_BELOW_MIN`.

## 1. Why this quarry exists

The durable release-safe coverage gate currently has enough `GLASS_SHATTER` quantity and grouping, but 237 of 242 positive assets come from the underlying `FREESOUND` family. That is approximately 97.93%, above the frozen 80% maximum. `GLASS_SHATTER` hard negatives also have only one credited underlying family (`SONYC_UST`).

Adding another Freesound wrapper, FSD50K view, re-host or mirror cannot solve either source-diversity problem. Source credit follows acoustic origin, not URL, host or dataset wrapper.

## 2. Candidate selected

Canonical source:

`https://opengameart.org/content/75-cc0-breaking-falling-hit-sfx`

The page identifies `rubberduck` as author, marks the submission `CC0`, and explicitly states that the author made 75 breaking/falling/hit sounds. This is materially different evidence from a re-host of Freesound-origin media.

A pinned public GitHub mirror is used only as byte transport:

- repository: `lavenderdotpet/CC0-Public-Domain-Sounds`;
- exact transport commit: `f2b6264f9ab89fabc266914c3654685d68c5a39b`;
- directory: `75-cc0-breaking-falling-hit-sfx`.

The mirror receives **zero** independent source credit. Canonical rights and provenance remain the OpenGameArt submission.

## 3. Semantic scope

Only six explicitly named `glass_breaking` files are positive candidates for `GLASS_SHATTER`.

`glass_falling`, `glass_hit`, rock, wood and metal break/impact rows are not promoted to the target. They are captured as target-specific hard-negative candidates where appropriate.

Filename evidence is sufficient to decide which rows may enter semantic review, not sufficient to grant final corpus admission. Real bytes, rights evidence, technical probe, canonical fingerprint, grouping and global dedup remain mandatory.

## 4. Conservative grouping

Variants are grouped by action/material family rather than counted as one independent group per file. Examples:

- `bfh1:glass_breaking`;
- `bfh1:glass_falling`;
- `bfh1:glass_hit`;
- `bfh1:rock_breaking`;
- `bfh1:rock_falling`;
- `bfh1:metal_hit`;
- `bfh1:wood_hit`.

This intentionally sacrifices apparent group count to prevent variant inflation.

## 5. Expected value if real-byte evidence passes

The first bounded acquisition contains:

- 6 `GLASS_SHATTER` positive candidates;
- at least 20 `GLASS_SHATTER` hard-negative candidates;
- at least 10 conservative hard-negative recording-family candidates;
- one candidate acoustic-origin family: `OPENGAMEART_RUBBERDUCK`.

This is expected to be enough to investigate closure of the second hard-negative source-family requirement for `GLASS_SHATTER`, subject to final admission and global dedup.

It is **not** enough by itself to solve positive source concentration. With the current 237 Freesound positives, substantially more non-Freesound positive assets are still required to bring the dominant-source fraction to <= 0.80.

## 6. Rejected shortcuts

The following are explicitly forbidden:

- counting the GitHub mirror as a source separate from OpenGameArt;
- counting OpenGameArt as a generic platform family when upstream audio came from elsewhere;
- coercing glass hits/falls into glass-shatter positives;
- counting every numbered variation as an independent recording group without defensible evidence;
- admitting a candidate because it downloads successfully;
- changing the 80% concentration floor to fit available data.

## 7. Execution chain

```text
source-page evidence
  -> pinned transport bytes
  -> SHA-256 + ffprobe
  -> canonical fingerprint
  -> durable acquisition report
  -> source-family / semantic review
  -> canonical ledger augmentation
  -> global grouping + dedup
  -> deterministic split
  -> coverage gate
```

Only the last coverage result can change `CERT-MK1-DF-CORPUS-001` eligibility.

## 8. Next quarry targets

After this acquisition is empirically materialized, continue specifically on the still-open critical-path deficits:

1. additional independent `GLASS_SHATTER` positives until source concentration is <= 0.80;
2. exact release-safe `FIRE_ALARM` positives with enough independent groups and all three development splits;
3. exact release-safe `TIRE_SQUEAL` positives and target-specific hard negatives;
4. independent hard-negative families for `FIRE_ALARM`, `SIREN`, `VEHICLE_HORN` and `TIRE_SQUEAL`;
5. at least two additional defensible background source families beyond `SONYC_UST`.

The Foundry is not reopened for structural redesign. Every next change must reduce an empirical coverage deficit or close its downstream freeze/certificate consequence.
