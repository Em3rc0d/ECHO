# MK2 Scale Plan

**Status:** `DECISION_FRAMEWORK / TO FREEZE FROM CAPACITY`

## Principle

Scale only the bottleneck demonstrated by evidence. Architectural sophistication is a cost and failure surface.

## Stage 0 — single host

Shared bounded inference workers, per-source supervisors, local/remote broker. Preferred while SLOs/capacity fit.

## Stage 1 — process isolation

Separate decoder/source workers from model inference when native decoder failures, CPU contention or model memory sharing require it.

## Stage 2 — multi-inference worker/accelerator

Partition/balance inference work across processes/GPUs. Preserve source fairness/order metadata.

## Stage 3 — distributed hosts

Introduce durable queue/service discovery only when source/site count, availability or hardware layout justifies networked scheduling.

## Scale triggers

Sustained queue lag, SLO breach before target N, accelerator saturation, decoder CPU saturation, memory duplication, host availability requirement or multi-site isolation.

## Anti-pattern

Do not jump directly to Kafka/Kubernetes/microservices because they are scalable technologies; scale topology must improve a measured constraint.

## Validation

Every scale stage reruns quality, latency, fairness, failure and security tests because distributed timing/retry can change event behavior.

## Rollback

Keep previous simpler topology deployable until new topology is certified.