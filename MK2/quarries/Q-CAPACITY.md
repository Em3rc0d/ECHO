# Quarry — Capacity and Scalability

**Status:** methodology `CERTIFIED`; capacity numbers `EMPIRICAL_MK2`.

## 1. Purpose

Determine how many concurrent sources a specific ECHO deployment can support while meeting latency, drop-rate and resource SLOs. Capacity is always expressed for a named hardware/model/configuration tuple.

## 2. Capacity tuple

A claim is invalid without:

```text
hardware CPU/GPU/RAM
OS/runtime/container versions
model + precision/quantization
window/hop
source codec/input rate
worker count
batching policy
queue/buffer config
Event Engine config
broker/event-store config
```

## 3. Load ladder

Run increasing source counts, for example 1/2/4/8/... until a constraint is violated. These are test points, not promises.

At each level measure:

```text
CPU/GPU/RAM
windows/s
queue lag p50/p95/p99
stale/drop rate per source
end-to-end latency p50/p95/p99
reconnect/error rate
broker publish latency
thermal behavior
```

## 4. Saturation definition

Saturation is not simply 100% CPU. It is the first load where one or more product SLOs fail or system behavior becomes unstable. Keep headroom instead of certifying at the absolute cliff.

## 5. Fairness

Report per-source distributions, not only aggregate throughput. One source must not remain healthy while others starve.

## 6. Soak

Short bursts can hide memory leaks, thermal throttling, reconnect churn and queue growth. Capacity certification therefore requires a soak duration appropriate to the target deployment.

## 7. Failure injection under load

At near-certified load test:

- source reconnect;
- broker restart;
- worker restart;
- burst of simultaneous acoustic events;
- slow event-store/subscriber;
- one malformed/noisy stream.

## 8. Scale-out decision

Only introduce external queues/distributed inference when single-node evidence shows it is necessary or operational requirements demand HA. Complexity is not a scalability metric.

## 9. Output

Publish a capacity envelope rather than “supports N cameras”:

```text
configuration X
certified <= N sources
under source profile Y
meeting SLO profile Z
with measured headroom H
```
