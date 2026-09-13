# Data Foundry — Metadata Intake

**Status:** `IMPLEMENTED`

## Purpose

Metadata intake converts source-specific annotations and release metadata into the dataset-neutral `RawAssetCandidate` contract without making semantic or legal assumptions. Parsing and admission are deliberately separate so an adapter cannot silently turn a source label into an ECHO truth label.

## Adapter boundary

```text
source release metadata
      ↓ source-specific parser
RawAssetCandidate
      ↓ canonical candidate JSONL
Foundry admission
```

Implemented adapters:

- FSD50K ground truth + vocabulary + optional clip metadata;
- SONYC-UST annotations;
- SINGA:PURA metadata + strong-label CSVs;
- ESC-50 metadata;
- UrbanSound8K metadata.

## Config-driven execution

Each intake run is described by `echo.intake-spec.v1`:

```json
{
  "schema_version": "echo.intake-spec.v1",
  "adapter": "sonyc",
  "parameters": {
    "csv_path": "/data/sonyc/annotations.csv",
    "audio_root": "/data/sonyc/audio"
  }
}
```

Run:

```bash
echo-data-foundry intake intake-sonyc.json work/sonyc-candidates.jsonl
```

The output is sorted canonically by `asset_id`; identical inputs therefore produce the same candidate-manifest SHA-256 independent of source iteration order.

## Candidate contract

The candidate preserves source identity and uncertainty, including source/release/asset ID, local path, exact upstream license string, original labels, label provenance, group/source/site/device IDs, upstream split, optional duration/sample-rate/channels and source-specific extra metadata.

`original_labels` are never replaced by ECHO labels during intake.

## FSD50K parsing rule

FSD50K labels are reconstructed from AudioSet MIDs and the release vocabulary when available. Human-readable labels may contain commas, so naive comma splitting of display names is forbidden.

## Group identity

Adapters preserve the strongest available relation that indicates samples should not be separated across protected splits. Examples include original Freesound source/uploader, sensor ID, recording/session or occurrence ID. Missing group evidence is surfaced to quality/admission rather than guessed away.

## Output evidence

Each execution records the intake spec, spec digest, candidate count, candidate-manifest digest and source release identity. These become upstream inputs to admission.

## Stop-the-line

Unknown adapter, malformed metadata, missing required source identity or a parser change that alters candidate semantics requires a new intake run. Candidate JSONL is an intermediate artifact and is never treated as an admitted corpus.

## Invalidation

Source metadata format/release, adapter parsing behavior or group-identity semantics changing invalidates the affected candidate manifest and all downstream records derived from it.
