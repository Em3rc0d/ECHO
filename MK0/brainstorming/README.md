# MK0 / Brainstorming

**Status:** `CERTIFIED_INPUT_TO_DESIGN`

## Purpose

Brainstorming establishes the problem space before choosing architecture. It asks what ECHO must detect/classify, what the acoustic evidence can and cannot prove, which environments matter, what constraints could make the project infeasible and which hypotheses must be tested later.

## Inputs

Project promise, initial user/professor context, state-of-art discovery and the anti-scope rule that acoustic classification must not be inflated into incident/crime interpretation.

## Artifacts

`PROBLEM-LANDSCAPE.md` frames the real engineering problem. `HYPOTHESES-REGISTER.md` separates assumptions from facts. `ANTI-SCOPE.md` prevents scope creep and semantic overclaiming.

## Key synthesis

The hard problem is not producing a label from a WAV file; it is sustaining useful event detection under noise, domain shift, weak camera microphones, continuous streams, multiple sources and false-positive pressure. Therefore real-world false alarms, domain holdout and streaming behavior are first-class concerns from the beginning.

## Output gate

Brainstorming is sufficient when design can state a bounded system, candidate taxonomy, non-functional drivers and explicit external/empirical unknowns without inventing answers.

## Invalidation

Reopen if the product promise, intended deployment environment or definition of an acoustic event changes materially.