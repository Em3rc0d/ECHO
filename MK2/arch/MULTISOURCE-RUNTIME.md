# MK2 Multi-Source Runtime

**Status:** `REFERENCE_DESIGN / CAPACITY_PENDING`

## Topology

Each source has independent supervisor/decoder/buffer/window state. Shared scheduler dispatches source-tagged windows to bounded model workers. EventEngine state remains `(source,event_type,generation)` scoped.

## Scheduler

Use per-source queue limits and fair dispatch. Weights may reflect configured service classes but must not silently starve standard sources. Exact algorithm is benchmarked under representative source rates.

## Worker model

Options: shared in-process pool, separate inference process(es), GPU-serving process or distributed workers. Choose from profiling of model thread/process safety, memory duplication, accelerator utilization and failure isolation.

## Ordering

Guarantee per-source sequence handling needed by EventEngine; no global total ordering is required for basic classification. Cross-source correlation consumers rely on UTC/source timestamps and documented uncertainty.

## Dynamic lifecycle

Sources can enable/disable/reconnect without restarting entire fleet. Config changes are validated/versioned; rolling source changes must preserve state semantics.

## Capacity

Sustainable N is measured at a defined source window rate, model/config/hardware, soak duration and SLO. Report fairness/lag/drop distribution by source, not only aggregate throughput.

## Failure isolation

One decoder/stream can crash/reconnect while shared inference remains healthy. Worker crash handling must not replay stale generations into new state.

## Invalidation

If selected model/device cannot share workers safely or source rates vary radically, adjust topology but keep contracts.