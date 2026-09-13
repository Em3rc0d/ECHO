# MK2 / Architecture

**Status:** `TARGET_ARCHITECTURE_SPECIFIED / FINALIZE_FROM MK1 CAPACITY`

## Purpose

Harden MK1 boundaries into a production-capable multi-source runtime with explicit backpressure, resilience, observability, security and event-delivery semantics.

## Core principle

Scale topology is evidence-driven. Start with the simplest architecture meeting frozen SLOs; introduce distributed queues/workers only when capacity/resilience requirements justify operational complexity.

## Artifacts

`MULTISOURCE-RUNTIME.md`, `BACKPRESSURE.md`, `EVENT-DELIVERY.md`, `DEPLOYMENT.md`, `RESILIENCE.md`, `OBSERVABILITY-ARCH.md`, `SECURITY-ARCH.md`.

## Invariants inherited

Source identity/state isolation, versioned contracts, bounded memory, no direct model->alert coupling, privacy by default and reproducible model/config release.

## Invalidation

MK1 measurements can change worker/process deployment, not the fixed promise.