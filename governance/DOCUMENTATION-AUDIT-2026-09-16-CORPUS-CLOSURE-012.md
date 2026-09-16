# Documentation Audit — Corpus Closure 012

**Date:** 2026-09-16  
**Certificate:** `CERT-DOC-012`  
**Status:** `CERTIFIED`  
**Scope:** durable post-Freesound MK1 corpus-closure truth before PR #37 grouping semantics are merged  
**Global invariant:** `ECHO-FREE-TIER-001`

## Audited baseline

`main@48af9f220b30f2197aa376bff025195cb0a2a13b`

Machine-readable readiness:

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
evidence_identity_sha256 = 85dee5596dbc9c88e0430e32b5e8eec7c014d526d132974542b2e4a36a108a50
CERT-MK1-DF-CORPUS-001 = OPEN
modeling_allowed = false
```

Canonical ledger:

```text
baseline_commit = 050f2ebc39fea0d1e6903190ad471fd97d1487dc
entry_count = 1141
canonical fingerprints = 1141 / 1141
missing fingerprints = 0
ledger blockers = 0
ledger_sha256 = 1ab3712452f42205fe9004f1d6cb9e778297487891bb373e5c42d635854f1d85
```

The reduction from the prior 1162-row snapshot is accepted as fail-closed revalidation: the fresh release-safe Freesound materialization changed the currently supportable durable evidence set. No prior row is grandfathered solely to preserve counts.

## Structural truth

```text
global dedup = PASS
recording-family audit = PASS
split integrity = PASS
protected split conflicts = 2
quarantined assets = 93
eligible development assets = 1048
content merge/delete = false
coverage = FAIL / 16 detailed gaps
freeze #1 = FAIL / gated
freeze #2 = FAIL / gated
reproducibility = FAIL / gated
```

The current 91-asset quarantine component is retained as authoritative durable evidence. This audit does not remove, remap or relabel it.

## Coverage truth

```text
BACKGROUND 416 assets / 383 groups / 4 sources PASS

FIRE_ALARM
  19 assets / 16 groups / 460.864037 s / 3 sources
  BIGSOUNDBANK 4 / FREESOUND 12 / WIKIMEDIA_COMMONS 3
  train 17/14, validation 2/2, test 0/0
  HN 202/202/4 PASS

GLASS_SHATTER
  222 assets / 205 groups / 4 sources
  BIGSOUNDBANK 6 / FREESOUND 209
  OPENGAMEART_RUBBERDUCK 6 / OPENGAMEART_TILL_BEHREND 1
  largest-source fraction 0.941441 FAIL <= 0.80
  HN 428/408/2 PASS

SIREN
  169 assets / 169 groups
  HN 235/235/4 PASS

TIRE_SQUEAL
  14 assets / 10 groups / 344.600098 s / 2 sources
  BIGSOUNDBANK 5 / FREESOUND 9
  train 11/8, validation 0/0, test 3/2
  HN 25/12/2 PASS

VEHICLE_HORN
  235 assets / 235 groups
  HN 142/142/3 PASS
```

Asset-quality stop lines remain zero for unknown licenses, missing provenance, invalid probes, non-positive duration, exact duplicate groups and final near-duplicate groups.

## Detailed coverage gaps

Exactly 16 remain:

```text
FIRE_ALARM_ASSETS_BELOW_MIN
FIRE_ALARM_GROUPS_BELOW_MIN
FIRE_ALARM_TEST_ASSETS_BELOW_MIN
FIRE_ALARM_TEST_GROUPS_BELOW_MIN
FIRE_ALARM_TRAIN_ASSETS_BELOW_MIN
FIRE_ALARM_VALIDATION_ASSETS_BELOW_MIN
FIRE_ALARM_VALIDATION_GROUPS_BELOW_MIN
GLASS_SHATTER_SOURCE_CONCENTRATION_TOO_HIGH
TIRE_SQUEAL_ASSETS_BELOW_MIN
TIRE_SQUEAL_GROUPS_BELOW_MIN
TIRE_SQUEAL_TEST_ASSETS_BELOW_MIN
TIRE_SQUEAL_TEST_GROUPS_BELOW_MIN
TIRE_SQUEAL_TRAIN_ASSETS_BELOW_MIN
TIRE_SQUEAL_TRAIN_GROUPS_BELOW_MIN
TIRE_SQUEAL_VALIDATION_ASSETS_BELOW_MIN
TIRE_SQUEAL_VALIDATION_GROUPS_BELOW_MIN
```

## Readiness gaps

```text
CORPUS_CERTIFICATE_NOT_CERTIFIED
COVERAGE_GATE_GAP_CODES_NOT_EMPTY
COVERAGE_GATE_NOT_PASS
COVERAGE_GATE_STATUS_NOT_PASS
FIRE_ALARM_ASSETS_19_LT_50
FREEZE_1_VALIDATION_NOT_PASS
FREEZE_2_VALIDATION_NOT_PASS
REPRODUCIBILITY_NOT_PASS
TIRE_SQUEAL_ASSETS_14_LT_50
```

## PR #37 candidate boundary

PR #37 changes the implementation of `MK1-NEAR-DUP-001` so the broad RMS-envelope threshold remains screening evidence and only separately confirmed edges can force shared split protection. The current durable 93-asset quarantine is **not** retrospectively altered by this documentation certificate. No recovered asset/group credit is claimed until the policy/code change is merged and the complete canonical-ledger → grouping → dedup → split → coverage → readiness cascade persists new evidence.

## Product/release law

The immutable promise remains unchanged:

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

```text
NO CERT-MK1-DF-CORPUS-001
=
NO Benchmark A/B/C
NO model winner
NO threshold calibration
NO replay progression
NO real-camera progression
```

`CERT-DOC-012` certifies documentation alignment only. It does not certify the corpus, model, thresholds or product release.
