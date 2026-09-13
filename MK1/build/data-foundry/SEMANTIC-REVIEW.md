# Data Foundry — Semantic Review Governance

**Status:** `IMPLEMENTED`

## Purpose

Semantic review resolves asset-level ambiguity without weakening the frozen acoustic taxonomy. Review is required when a source label is broader or ambiguous but may contain a valid ECHO target. The reviewer confirms observable sound evidence; they do not infer incidents, intent or legal meaning.

## Review contract

Machine-readable decisions use `echo.review-decisions.v1` and contain:

```text
asset_id
approved
approved ECHO labels
reviewer identity
reviewed_at_utc
rationale
evidence_ref (optional)
```

The empty governed template lives at `configs/data_foundry/review_decisions.v1.json` and is validated by `schemas/data_foundry/review-decisions.schema.json`.

## Allowed effect

A positive review may resolve a `BROADER`/`AMBIGUOUS` mapping into explicit ECHO labels for that asset. A rejection keeps the asset quarantined with `MANUAL_REVIEW_REJECTED`.

Review **cannot**:

- override an incompatible/unknown license;
- fabricate missing file/provenance/group identity;
- move field holdout into training;
- bypass hashing, duplicate audit or split rules;
- create labels outside the frozen MK1 taxonomy.

## Example

A FSD50K asset carrying source label `Shatter` is broader than `GLASS_SHATTER`. It remains quarantined as a positive until a review decision confirms that glass shattering is actually audible. Generic `Alarm` cannot become `FIRE_ALARM` merely because the reviewer expects an alarm-like sound; evidence must support the narrower acoustic phenomenon.

## Reproducibility

Review files are versioned inputs. The final asset record stores the review decision metadata in `extra.manual_review`. Changing a review decision creates a new asset-record manifest and therefore a new corpus identity.

## QA

Priority review queues should include all broad/ambiguous positive candidates, label conflicts, high-loss examples and later high-confidence false positives used for hard-negative mining. Sampling review of exact mappings remains useful for source-quality audits.

## Stop-the-line

Missing reviewer/rationale/timestamp, duplicate conflicting decisions or an out-of-taxonomy label is a hard error. Review evidence that cannot be reconstructed invalidates the affected asset decision.
