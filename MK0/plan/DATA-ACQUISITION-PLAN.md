# Data Acquisition Plan — MK0

**Status:** `CERTIFIED_POLICY / MK1 MANIFEST PENDING`

## Objective

Create a reproducible, legally traceable corpus for the MK1 taxonomy without mixing training evidence, test evidence and real-field holdout.

## Source tiers

`TIER-0` public ontology/pretraining references such as AudioSet.  
`TIER-1` admissible licensed clips from environmental datasets such as filtered FSD50K and task-specific sources.  
`TIER-2` academic benchmark-only datasets whose terms/domain make them unsuitable as unrestricted product corpus.  
`TIER-3` ECHO field recordings from actual hardware/site, only when authorized.

## Admission pipeline

```text
source discovery
 -> license/provenance check
 -> download/capture
 -> SHA-256
 -> semantic label mapping
 -> quality/duplicate review
 -> recording_group assignment
 -> split assignment
 -> immutable manifest version
```

Unknown license/provenance means quarantine, not optimistic inclusion.

## Split policy

Keep related assets together by original recording/event/session/uploader/site/device as applicable. Field holdout never participates in training, early stopping or threshold calibration.

## Positive data

Each target class must report independent groups, source diversity, total duration/event counts, license distribution and ambiguity rate—not only clip count.

## Negatives

Acquire broad background plus class-specific confusers. Long continuous negative recordings are required to estimate false alarms/source-hour. Hard-negative mining may iteratively add reviewed false positives to future training sets while preserving frozen test/holdout.

## Field capture

When authorized, capture actual codec/device/environment metadata and a matrix of distance/noise/orientation conditions. Do not assume safe/feasible generation of every target event; recorded/replayed licensed examples may supplement controlled field tests.

## Outputs

`dataset-manifest`, mapping report, split audit, license inventory, duplicate audit and field-holdout manifest.

## Invalidation

A taxonomy or licensing change requires rebuilding affected manifest sections and reviewing downstream benchmark hashes.