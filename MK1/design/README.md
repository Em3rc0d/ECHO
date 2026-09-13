# MK1 / Design

**Status:** `CLOSED_FOR_BUILD`

## Purpose

Specify observable behavior and versioned contracts for the first vertical before implementation. Design is implementation-agnostic: it defines source/audio/event semantics, requirements, taxonomy, privacy, observability and temporal rules.

## Inputs

Certified MK0 boundary, taxonomy, data policy, benchmark protocol and source/PubSub research.

## Key artifacts

`REQUIREMENTS.md`, `SOURCE-CONTRACT.md`, `AUDIO-CONTRACT.md`, `TAXONOMY.md`, `CONTRACTS.md`, `EVENT-LIFECYCLE.md`, `EVENT-ENGINE.md`, `OBSERVABILITY.md`, `PRIVACY-SECURITY.md`.

## Design invariants

`source_id` is mandatory end-to-end. Audio is normalized under a versioned contract. Multi-label scores remain separate from confirmed events. Thresholds are configuration/evidence, not embedded constants. Event delivery is independent from model internals. Raw audio retention is off by default.

## Output to architecture

Architecture may choose process/task/worker topology but cannot violate these contracts without reopening design.

## Invalidation

Taxonomy, source/audio envelope or lifecycle/schema changes require dependent architecture/build review.