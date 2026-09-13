# ECHO Research Source Catalog

**Status:** `CERTIFIED_MK0_CATALOG / EXTENDABLE`

## Purpose

Provide a curated map of authoritative sources used by ECHO. The catalog is organized by the claim each source can support, not by search-engine popularity.

## Source tiers

`T1 PRIMARY`: standard, official docs, original paper/repo, official dataset release, normative authority.  
`T2 OPERATIONAL`: original docs of a related deployed/open project.  
`T3 SECONDARY`: explanatory material used only when T1/T2 do not directly answer a contextual question.

## Models

TensorFlow YAMNet transfer-learning documentation and model source; PANNs paper/repository; AST paper/repository; HTS-AT repository/paper; PaSST and BEATs original papers/repositories when promoted. Exact checkpoint pages/licenses are added to model manifests.

## Datasets/evaluation

AudioSet official site/ontology; FSD50K official Zenodo release; ESC-50 official repo; UrbanSound8K official distribution; SONYC-UST official Zenodo; DCASE challenge/task/metric pages; release-specific DESED/MIMII sources.

## Streaming/cameras

ONVIF Profile T/media specs; FFmpeg protocol documentation; GStreamer `rtspsrc` docs; actual camera manufacturer documentation after model is known.

## Messaging

OASIS MQTT 5.0 specification; Eclipse Mosquitto official docs/project; related-system MQTT docs such as Frigate for operational patterns.

## Privacy/compliance

Peru ANPD official legal/normative/publication sources for personal data/videovigilance context; deployment may require additional institutional review.

## Licensing

Original repository LICENSE files, package metadata, checkpoint release terms and dataset/asset license metadata. Never infer checkpoint or media rights from surrounding source-code license.

## Catalog record format

```yaml
source_id: EV-...
tier: T1|T2|T3
canonical_uri: ...
publisher: ...
release_or_access_context: ...
claim_supported: ...
limitations: ...
license_relevance: ...
downstream_artifacts: [...]
```

## Quality rule

A URL in the catalog is not automatically evidence for every related claim. Each citation is scoped to what the source states or reasonably supports.

## Maintenance

New source -> stable ID. Corrected/superseded source -> new record plus impact review. Dead URLs are replaced with canonical archived/official equivalents when possible without rewriting history.