# ECHO Documentation Audit — Corpus Closure 012

**Certificate:** `CERT-DOC-012`  
**Status:** `CERTIFIED`  
**Audit date:** 2026-09-16  
**Audited durable readiness commit:** `48af9f220b30f2197aa376bff025195cb0a2a13b`  
**Global invariant:** `ECHO-FREE-TIER-001`

## Scope

This audit recertifies repository documentation after the SHA-bound Freesound orchestration hardening, explicit FIRE/TIRE semantic curation, live release-safe Freesound rematerialization, canonical-ledger rebuild and complete closure/readiness cascade. It supersedes `CERT-DOC-011` only for documentation truth; it does not certify the corpus, the model or any downstream runtime stage.

## Immutable product promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

Camera, RTSP/ONVIF, MQTT, dashboards, persistence and alerts remain supporting capabilities. They do not redefine the acoustic detection/classification core and remain downstream of the required corpus/model gates.

## Audited corpus evidence

```text
readiness commit          48af9f220b30f2197aa376bff025195cb0a2a13b
readiness identity        85dee5596dbc9c88e0430e32b5e8eec7c014d526d132974542b2e4a36a108a50
ledger baseline           050f2ebc39fea0d1e6903190ad471fd97d1487dc
ledger entries            1141
fingerprints              1141 / 1141
ledger blockers           0
ledger sha256             1ab3712452f42205fe9004f1d6cb9e778297487891bb373e5c42d635854f1d85
coverage ledger sha256    72039f7f11b08fcadbe19ee1cf639f929491a67f59bce36d3ee953f366364f14
```

The lower ledger count versus DOC-011 is not data deletion performed to improve coverage. The live Freesound rematerialization re-resolved current release-safe pages/previews and some previously materialized Freesound rows no longer survived the current release-safe evidence path. ECHO accepted that external drift and rebuilt all downstream evidence instead of preserving stale credit.

## Structural gates

```text
global acoustic grouping    PASS
fallback assets after       0
global acoustic components  12
members reassigned          118
content merge/delete        false

global dedup                PASS
recording-family audit      PASS
split integrity             PASS
protected split conflicts   2
quarantined assets          93
eligible development assets 1048
```

No conflicting group was manually remapped or deleted to improve counters.

## Current final coverage

```text
BACKGROUND
  416 assets / 383 groups / 4 source families                    PASS

FIRE_ALARM
  19 assets / 16 groups / 460.864037 s / 3 source families
  BIGSOUNDBANK 4 / FREESOUND 12 / WIKIMEDIA_COMMONS 3
  train 17 assets / 14 groups
  validation 2 / 2
  test 0 / 0
  HN 202 assets / 202 groups / 4 source families                 PASS

GLASS_SHATTER
  222 assets / 205 groups
  BIGSOUNDBANK 6 / FREESOUND 209
  OPENGAMEART_RUBBERDUCK 6 / OPENGAMEART_TILL_BEHREND 1
  largest source fraction 0.941441                               FAIL <= 0.80
  HN 428 assets / 408 groups / 2 source families                 PASS

SIREN
  169 assets / 169 groups
  HN 235 assets / 235 groups / 4 source families                 PASS

TIRE_SQUEAL
  14 assets / 10 groups / 344.600098 s / 2 source families
  BIGSOUNDBANK 5 / FREESOUND 9
  train 11 assets / 8 groups
  validation 0 / 0
  test 3 assets / 2 groups
  HN 25 assets / 12 groups / 2 source families                   PASS

VEHICLE_HORN
  235 assets / 235 groups
  HN 142 assets / 142 groups / 3 source families                 PASS
```

The TIRE grouping reduction is intentional evidence quality: correlated Chrysler and Nordschleife series are conservatively grouped rather than counted as independent recording sessions.

## Coverage gap truth

Coverage remains `FAIL`, now with exactly **16** detailed gaps:

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

`FIRE_ALARM_TRAIN_GROUPS_BELOW_MIN` is durably closed. Background and every required hard-negative floor remain closed.

## Quality stop lines

Final coverage still reports zero:

- unknown licenses;
- missing label provenance;
- non-positive durations;
- invalid audio probes;
- exact duplicate groups;
- near-duplicate groups.

## Readiness and release law

```text
EMP-MK1-CORPUS-READINESS-001 = BLOCKED
eligible_for_certificate_review = false
CERT-MK1-DF-CORPUS-001 = OPEN
modeling_allowed = false
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
```

Exact readiness blockers remain nine, with current positive counters `FIRE_ALARM_ASSETS_19_LT_50` and `TIRE_SQUEAL_ASSETS_14_LT_50`.

The frozen law remains:

```text
NO CERT-MK1-DF-CORPUS-001
=
NO Benchmark A/B/C
NO YAMNet/PANNs/CNN model work
NO EMP-MODEL-001
NO threshold calibration
NO replay progression
NO real-camera progression
```

## Freesound audit conclusion

The SHA-bound orchestration behaved as designed:

1. semantic configuration changed;
2. release-safe materialization resolved live rights/pages/previews and real bytes;
3. fingerprints/probes were regenerated;
4. only durable evidence fed Canonical Ledger;
5. grouping/dedup/split/coverage/readiness were recomputed;
6. stale rows were not preserved merely to keep counts high.

The resulting decline in several Freesound-backed classes is therefore evidence of fail-closed operation, not a reason to relax the release-safe boundary.

## Authorized next work

The only authorized critical-path work remains corpus closure:

```text
independent exact FIRE positives/groups/split coverage
independent exact TIRE positives/groups/split coverage
non-Freesound GLASS positives sufficient for <=0.80 concentration
  ↓
coverage PASS / gap_codes=[]
  ↓
freeze #1
  ↓
freeze #2 clean
  ↓
reproducibility PASS
  ↓
CERT-MK1-DF-CORPUS-001
  ↓
modeling_allowed=true
  ↓
Benchmark A/B/C
```

Evidence-only source scouting/materialization may proceed before corpus admission, but it receives zero coverage credit until a reviewed registration/admission path and the full closure cascade succeed.

## Certification decision

`CERT-DOC-012 = CERTIFIED` for documentation truth at the audited durable evidence above.

`CERT-DOC-011` and `CERT-DOC-001..010` are historical/invalidated. `CERT-MK1-DF-CORPUS-001` remains OPEN. `CERT-MK1-DF-TOOLCHAIN-005` remains CANDIDATE. `CERT-MK1-DF-SONYC-001` remains independently CERTIFIED within scope.

Any change to durable ledger/closure/readiness evidence, promise, taxonomy, source identity, rights, semantic-review decisions, probe/fingerprint/group/dedup/split/coverage/freeze semantics, free-tier invariant or certificate state invalidates DOC-012 and requires re-audit.
