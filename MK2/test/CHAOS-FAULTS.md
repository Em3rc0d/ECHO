# MK2 Chaos / Fault Injection

**Status:** `CONTROLLED_STAGING_ONLY`

## Purpose

Test combinations/timing of faults that deterministic unit tests may miss. Chaos is not random destruction; each experiment has a hypothesis, blast radius and abort condition.

## Experiments

Repeated source flaps during high inference load; broker outage during event burst; one slow worker causing scheduler imbalance; process restart with queued old-generation work; network jitter/packet loss plus high background; storage slowdown plus broker retry; model service restart during concurrent sources.

## Guardrails

Run in staging/safe lab unless specifically approved. No destructive field event generation. Define maximum duration/resource/retention impact and restore procedure.

## Expected invariants

Bounded memory, source isolation, no cross-source event state, stable event ID semantics, observable degradation, controlled reconnect/backoff and recovery without hidden backlog.

## Evidence

Fault timeline, active release/config, metrics/log excerpts, SLO impact, invariant violations and corrective action.

## Promotion

A chaos scenario that finds a defect becomes a deterministic regression/fault test where practical.