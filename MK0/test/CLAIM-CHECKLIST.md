# Claim Checklist — MK0

**Status:** `PASS_WITH_EMPIRICAL_BOUNDARIES`

## Purpose

Prevent research notes from turning into unsupported project claims.

## Checklist per claim

- Is it `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION` or `TARGET`?
- Does a factual external claim cite a primary/official source when available?
- Does the source actually support the precise wording?
- Is release/version/date relevant and recorded?
- Is a dataset-level statement being incorrectly applied to every asset?
- Is a published benchmark being incorrectly presented as ECHO performance?
- Is a camera/protocol capability being assumed without the actual device?
- Is a social/causal interpretation being inferred from acoustic evidence?
- Is a numeric target clearly separated from a measurement?
- Does the claim have downstream dependencies requiring invalidation if it changes?

## High-risk claim examples

“YAMNet is best for ECHO” is invalid before benchmark. “YAMNet accepts 16 kHz mono in the referenced official implementation” can be factual. “ECHO detects glass at 25 m” is invalid before field evidence. “25 m is a planned test point” is a target/protocol statement.

## Pass evidence

MK0 certification specifically leaves model winner, thresholds, distance/SNR, final SLO and real-camera compatibility empirical/external.

## Failure handling

Downgrade unsupported statements to hypothesis/target, add provenance or remove them. If a claim supported a decision, re-evaluate dependent nodes.

## Invalidation

Re-run checklist on material edits to certified research/design artifacts.