# Research Plan — MK0

**Status:** `EXECUTED / MAINTAINED_FOR_TRACEABILITY`

## Objective

Reduce uncertainty in an order that minimizes rework. Research is not a broad literature survey for its own sake; every quarry must feed a design/architecture decision, benchmark protocol or explicit external gate.

## Workstreams

1. **Problem/taxonomy:** verify target acoustic semantics and confusers without inferring social incidents.
2. **Data:** identify datasets/releases, label mappings, licenses, leakage risks and field-data need.
3. **Models:** compare pretrained CNN/transformer/self-supervised families and deployment implications.
4. **Streaming/source:** research RTSP, ONVIF, decoders, codecs, reconnect and camera limitations.
5. **Event semantics:** distinguish model windows from physical events and design temporal aggregation.
6. **Pub/Sub:** evaluate delivery semantics and broker candidates.
7. **Multi-source:** concurrency, bounded queues, fairness and source health.
8. **Robustness/OOD:** noise, domain shift, hard negatives, calibration and abstention.
9. **Security/privacy/licensing:** credentials, media retention, supply chain and dataset rights.

## Evidence priority

Primary standards/docs and original papers/repos outrank derivative blogs. Dataset facts come from official release pages/DOIs. Related systems can validate operational patterns but do not prove ECHO performance.

## Extraction format

Each finding records source, date/release when relevant, claim, evidence type, confidence, ECHO implication and whether it is FACT/EVIDENCE, INFERENCE or DECISION CANDIDATE.

## Closure rule

A research line closes when all architecture-changing uncertainty is either supported by evidence, turned into a controlled MK1 experiment or isolated as `EXTERNAL_GATE_OPEN`.

## Anti-patterns

Do not choose a model from leaderboard accuracy, treat dataset label names as semantic equivalence, assume “open source = unrestricted”, promise source count/distance without hardware, or mark a design protocol as a measured result.

## Invalidation

New primary evidence or changed release/license can reopen the affected quarry without invalidating unrelated work.