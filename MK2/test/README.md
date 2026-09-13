# MK2 / Test

**Status:** `SPECIFIED / EXECUTION GATED`

## Purpose

Certify the declared production profile rather than merely re-running MK1 unit tests. MK2 test stresses capacity, time, faults, model regression, delivery, security and release reproducibility under sustained conditions.

## Test layers

Regression -> load/capacity -> soak -> resilience/fault/chaos -> model/field regression -> security/privacy -> migration/rollback -> release certification.

## Evidence identity

Every run references release candidate digest, deployment profile, active model/config/schema, source/load generator manifest and hardware/environment.

## Failure discipline

A failed SLO remains FAIL until corrected or governance explicitly versions the SLO/profile. Tests are not retroactively redefined to fit observed behavior.

## External gates

Production claims involving real cameras/sites require those hardware/privacy/network gates closed. Synthetic load can certify architecture capacity but not acoustic field quality.

## Exit

`MK2 RELEASE CERTIFIED` only after all blocking tests and release BOM/provenance gates pass.