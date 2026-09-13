# MK2 / Brainstorming

**Status:** `PREPARED / AWAITS MK1 MEASUREMENTS`

## Purpose

Identify production/hardening questions that MK1 evidence must answer before MK2 design freezes. Unlike MK0 brainstorming, this phase starts from a working vertical and asks what breaks under sustained/multi-source/operational conditions.

## Workstreams

Production goals, scaling hypotheses and operations scenarios cover capacity, failure domains, maintainability, cost, drift and release behavior.

## Evidence dependency

Do not hardcode “supports 10 cameras” or “<2 s p95” here. Those become targets only after MK1 supplies model throughput, event latency and source-domain results.

## Exit

Brainstorming closes when MK1 evidence is translated into explicit production hypotheses and the design can define SLO/model/retention contracts.

## Invalidation

New deployment profile or major MK1 model/runtime change reopens relevant assumptions.