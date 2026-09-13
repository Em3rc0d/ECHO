# Quarry — Thresholds and Temporal Parameters

**Status:** `PROTOCOL_CERTIFIED / VALUES_PENDING`

## Purpose

Derive numerical decision parameters from validation evidence instead of defaulting to 0.5 or tuning against test/demo examples.

## Parameters

Per-class entry/exit score threshold, optional calibrator, temporal M-of-N/evidence duration, max gap, merge/dedup window and cooldown/rearm.

## Procedure

Use validation predictions/stream replays to generate class PR curves and operational event curves. Choose candidate operating points according to frozen priorities such as critical recall and acceptable false alarms/source-hour. Fit calibrator only on validation if used.

## EventEngine interaction

Window threshold and temporal confirmation are coupled: lowering score threshold plus stronger temporal evidence may outperform a high score threshold. Tune/evaluate the pair as a configuration, not independently while peeking at test.

## Hysteresis

Entry threshold may exceed exit threshold to avoid rapid state oscillation. Exact values are class-specific empirical outputs.

## Final test

Freeze model + calibrator + EventEngine config, then evaluate untouched test/field holdout once for certification. A failure leads to a new experiment/version, not silent retuning on the test result.

## Output

Versioned threshold/EventEngine config with validation rationale and hash.

## Invalidation

Model, preprocessing, taxonomy or domain calibration change requires threshold re-evaluation.