# MK1 / Test

**Status:** `SPECIFIED / EXECUTION_PENDING_BUILD`

## Purpose

Turn the first implementation into evidence. Tests cover scientific validity, model quality, continuous-stream behavior, runtime, contracts, source isolation, delivery, failure recovery and privacy/security.

## Layers

Unit/contract -> integration -> offline model benchmark -> streaming replay -> multi-source/fault -> MQTT E2E -> real-camera/field branch -> final certification.

## Evidence rule

Every test result cites build/config/data/model identity. Protocol-only documents never receive PASS on behalf of an unexecuted test.

## Core outputs

Per-class metrics, false alarms/source-hour, misses, latency/resources, calibration, event fragmentation/duplicates, source isolation, reconnect/delivery evidence, security/privacy checks and known limitations.

## External branch

Camera/field tests remain pending until external gate closes; replay tests can still certify the core vertical.

## Exit

MK1 certificate only after Definition of Done evidence is satisfied or an explicit failure/reasoned deferral is recorded.