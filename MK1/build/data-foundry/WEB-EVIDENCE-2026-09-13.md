# MK1 Data Foundry — Web Evidence Audit 2026-09-13

**Status:** `EVIDENCE_CAPTURED / ASSET-LEVEL EXECUTION PENDING`

## Purpose

Record source-level facts used to design the Foundry. These facts justify source roles and mappings; they do not replace local acquisition, per-asset review or benchmark evidence.

## FSD50K

Primary release: https://zenodo.org/records/4060432  
Companion explorer: https://fsannotator.upf.edu/fsd/release/FSD50K/

Evidence captured:

- 51,197 human-labelled Freesound clips; 200 released classes; over 100 h.
- official release documents mixed clip licenses: CC0, CC-BY, CC-BY-NC and CC Sampling+; per-clip license metadata is supplied.
- companion release table currently exposes `Shatter` (510), `Siren` (132), and `Vehicle horn, car horn, honking` (183) among released classes.
- the release table does not list `Fire alarm` or `Tire squeal` among the final 200 classes, so AudioSet ontology membership must not be confused with FSD50K-release availability.

Foundry consequence: asset-level rights filter; `Shatter` requires glass-specific review; siren/horn are direct candidates.

## AudioSet

Ontology: https://research.google.com/audioset/ontology/  
Relevant ontology pages include direct concepts for `Shatter`, `Siren`, `Fire alarm`, `Vehicle horn, car horn, honking`, and `Tire squeal`.

Evidence captured at audit time:

- `Shatter`: 368 annotations;
- `Siren`: 8,498;
- `Fire alarm`: 921;
- `Vehicle horn, car horn, honking`: 3,707;
- `Tire squeal`: 1,557.

AudioSet's media is YouTube-derived. ECHO therefore treats ontology/annotation facts separately from rights/availability of underlying media.

Foundry consequence: `reference_only` raw-media posture by default; pretrained-model provenance and ontology mapping remain useful.

## SONYC-UST

Release evidence: https://zenodo.org/records/3966543

Evidence captured:

- real urban acoustic sensor network;
- multilabel taxonomy with 23 fine classes / 8 coarse groups;
- alert-signal fine classes include car-horn, car-alarm, siren and reverse-beeper;
- v2 release family provides train/validation/test data and verified annotations, with sensor/time-aware split design;
- CC BY 4.0.

Foundry consequence: strong urban-domain source for `VEHICLE_HORN`, `SIREN`, alert confusers and long background/context; preserve sensor identity.

## SINGA:PURA

Release: https://zenodo.org/records/5645825

Evidence captured:

- 6,547 strongly-labelled recordings in the public strong-label subset;
- 10-second urban sensor recordings, with 1 or 7 channels depending on capture device;
- per-event onset/offset and sensor metadata;
- taxonomy includes `3-1 Glass breaking`, `5-1 Car horn`, `5-3 Siren`, plus friction-brake and generic screeching confusers;
- CC BY-SA 4.0.

Foundry consequence: direct temporal evidence for glass/horn/siren; ShareAlike review required for default release-safe lineage; brake/screech labels remain non-equivalent to tire squeal.

## ESC-50

Official repository: https://github.com/karolpiczak/ESC-50

Evidence captured:

- 2,000 five-second recordings;
- 50 classes, 40 examples/class;
- includes `Siren` and `Car horn`;
- audio WAV, 44.1 kHz mono in the published collection description;
- full ESC-50 uses CC BY-NC; ESC-10 subset has different terms.

Foundry consequence: `research_extended` sanity benchmark, not default release-safe training pool.

## UrbanSound8K

Reference: https://serv.cusp.nyu.edu/projects/urbansounddataset/urbansound8k.html

Evidence captured:

- 8,732 labelled urban excerpts, <=4 s, 10 classes;
- relevant classes: `car_horn`, `siren`;
- metadata exposes Freesound `fsID`, occurrence/slice IDs, salience and official folds;
- source audio technical properties can vary because excerpts retain original Freesound properties;
- CC BY-NC 3.0.

Foundry consequence: research-only urban contrast; preserve `fsID`/occurrence grouping and official fold evidence.

## Evidence classification

`FACT/EVIDENCE`: source-level release facts above.  
`INFERENCE`: how each source contributes to ECHO based on taxonomy/domain.  
`DECISION`: default source profile and mapping/admission policy.  
`OPEN`: exact admitted counts, independent groups, durations, duplicate clusters, class balance and sufficiency after local execution.

## Invalidation

Recheck this audit if upstream release/terms change or a newer source version is promoted into MK1. Asset-level manifests always take precedence over source-level headline counts.