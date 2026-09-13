# Dataset Sources — MK0

**Status:** `CERTIFIED_LANDSCAPE / ASSET_MANIFEST_PENDING`

## Purpose

Record official dataset releases and what they can legitimately contribute to ECHO. Dataset discovery is not equivalent to asset admission.

## AudioSet

Useful for ontology, pretrained-model provenance and target/confuser discovery. Media is YouTube-derived; ECHO does not infer redistribution rights for underlying media from metadata/ontology licensing.

## FSD50K

Large Freesound-derived multilabel environmental corpus. Valuable for positives/negatives, but per-clip mixed Creative Commons conditions require asset-level license filtering and provenance.

## ESC-50

Small, balanced environmental benchmark with useful classes such as siren/horn/glass-like categories depending on mapping. Its size and non-commercial conditions make it a sanity/research benchmark rather than unrestricted production corpus.

## UrbanSound8K

Urban clips useful for domain contrast and classes including siren/horn. Narrow taxonomy and curated clip structure limit its value as a continuous-deployment proxy.

## SONYC-UST

Real urban acoustic sensor network with multilabel annotations and site/sensor structure. Useful evidence for polyphony, urban background, domain/device separation and field-style evaluation methodology.

## DCASE / DESED

Task-specific releases support SED evaluation, strong/weak labels, overlapping events and PSDS-style methodologies. Each task/release has its own terms and domain.

## MIMII

Industrial machine audio can supply domain-shift/hard-negative research. Its anomaly-detection objective is not directly ECHO classification.

## ECHO Field Dataset

Future authorized recordings from actual camera/microphone/site. It is the decisive domain holdout but must preserve privacy/permission/retention metadata.

## Admission caveat

No asset enters MK1 because its dataset name appears here. `Q-DATASETS.md` defines semantic mapping, grouping, hashing, license and split requirements.

## References

Official release links are consolidated in `research/DATASET-MATRIX.md` and the dated web audit.