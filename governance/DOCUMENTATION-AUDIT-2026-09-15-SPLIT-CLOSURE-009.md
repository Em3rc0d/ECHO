# ECHO Documentation Audit — Split Closure 009

**Certificate:** `CERT-DOC-009`  
**Status:** `CERTIFIED`  
**Audit date:** 2026-09-15  
**Audited repository state:** `589e7f4affed39e1ffcf6f50602d79587560bbb3`  
**Markdown corpus:** `213 files`  
**Global ancestor:** `ECHO-FREE-TIER-001`

## Scope

This audit certifies documentation coherence after the protected split-conflict quarantine policy was executed against real corpus evidence. It does not certify final corpus coverage, freeze/reproducibility, the closure-era toolchain, or model entry.

## Exact empirical lineage

```text
PR #13 merge / implementation     03cd0627c9c6fcf0780d8d4ce48d5fa7f89fbd01
main Data Foundry CI              34971457870 PASS
main Documentation Governance     34971457752 PASS on pre-cascade docs
main Free-Tier Boundary           34971457814 PASS
closure evidence run              34971457662 PASS
closure evidence commit           205eb419b20f10461271ff1fbbd78eb3fa9560e9
readiness run                     34971547338 PASS
readiness evidence commit          589e7f4affed39e1ffcf6f50602d79587560bbb3
```

## Closed split node

`MK1-SPLIT-INTEGRITY-002` applies `quarantine_entire_recording_group` whenever a globally protected acoustic group spans incompatible recognized upstream splits.

Fresh evidence:

```text
split-integrity schema                    echo.split-integrity.v2
status                                    PASS
gap_codes                                 []
ready candidate assets                    1078
eligible development assets               1016
conflicting recording groups              3
conflicting groups quarantined             3
quarantined assets                        62
UNASSIGNED assets                          0
quarantine identity                       1679540dd50eea39200f95ee98130d2e38acd0d21ca73edf7eac04040bb42aaf
```

No individual clip was remapped. All 62 assets remain durable ledger/source evidence but are excluded from development coverage and frozen corpus membership.

The quarantined components are:

```text
global-acoustic:49755af077645d9cd379  2 assets  train+validation
global-acoustic:683a2c690a388e66903b  2 assets  test+train
global-acoustic:b0a528766144425812e3 58 assets  test+train+validation
```

## Upstream closure state

```text
canonical fingerprints       1081 / 1081
global dedup                 PASS
recording-family audit       PASS
split integrity              PASS
```

The canonical ledger still has exactly three non-admissible rows:

```text
LICENSE_NOT_RELEASE_SAFE = 1
SEMANTIC_STATUS_CONFLICT_FIRE_ALARM = 1
SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL = 1
```

They remain visible and fail-closed. No rights or semantic conflict has been coerced into corpus credit.

## Coverage truth after split quarantine

`coverage-gate.json` remains `FAIL`, but it no longer inherits a split failure. It evaluates 1016 development assets and excludes exactly 62 quarantined assets.

Key measured gaps:

```text
FIRE_ALARM       9 assets / 6 groups / 190.182749 s
TIRE_SQUEAL     11 assets / 11 groups / 280.544098 s
GLASS_SHATTER   242 assets, 237 FREESOUND / 5 BIGSOUNDBANK,
                largest source fraction = 0.979339 > 0.80
BACKGROUND      363 assets / 362 groups / 1 source family < 3
```

Hard-negative source/asset gaps remain for FIRE_ALARM, GLASS_SHATTER, SIREN, TIRE_SQUEAL and VEHICLE_HORN. TIRE_SQUEAL and VEHICLE_HORN still have zero governed hard-negative assets.

## Authoritative readiness

At `589e7f4affed39e1ffcf6f50602d79587560bbb3`:

```text
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
evidence_identity_sha256 = c20eab44bae7cb10e7038833fdf46741d9d4c1574ebfe1b65e47dd6db160249b
```

Exact readiness gaps are now 19:

```text
CORPUS_CERTIFICATE_NOT_CERTIFIED
COVERAGE_GATE_GAP_CODES_NOT_EMPTY
COVERAGE_GATE_NOT_PASS
COVERAGE_GATE_STATUS_NOT_PASS
FIRE_ALARM_ASSETS_10_LT_50
FIRE_ALARM_HARD_NEGATIVE_SOURCES_1_LT_2
FREEZE_1_VALIDATION_NOT_PASS
FREEZE_2_VALIDATION_NOT_PASS
GLASS_SHATTER_HARD_NEGATIVE_SOURCES_1_LT_2
LEDGER_LICENSE_NOT_RELEASE_SAFE_1
LEDGER_SEMANTIC_STATUS_CONFLICT_FIRE_ALARM_1
LEDGER_SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL_1
REPRODUCIBILITY_NOT_PASS
SIREN_HARD_NEGATIVE_SOURCES_1_LT_2
TIRE_SQUEAL_ASSETS_11_LT_50
TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20
TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2
VEHICLE_HORN_HARD_NEGATIVES_0_LT_20
VEHICLE_HORN_HARD_NEGATIVE_SOURCES_0_LT_2
```

`SPLIT_INTEGRITY_NOT_PASS` is closed by empirical evidence.

## Certification lineage

```text
CERT-DOC-008                INVALIDATED / historical
CERT-DOC-009                CERTIFIED / current
CERT-MK1-DF-TOOLCHAIN-004   INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005   CANDIDATE
CERT-MK1-DF-SONYC-001       CERTIFIED / scoped
CERT-MK1-DF-CORPUS-001      OPEN
```

## Next authorized closure work

1. Exclude or resolve the three non-admissible rights/semantic rows without deleting source evidence or coercing labels.
2. Acquire genuine independent real-media evidence for positive, source-concentration, background and hard-negative deficits.
3. Re-run dedup/group/split/coverage.
4. Only with coverage PASS may freeze #1/#2 and reproducibility become eligible.

## Non-claims

DOC-009 does not claim coverage PASS, final corpus membership, freeze/reproducibility PASS, model quality, threshold calibration, replay readiness, camera readiness, or final MK1 release.

## Invalidation

DOC-009 invalidates on any Markdown inventory change, material Foundry semantic change, new durable ledger/closure/readiness evidence, source/policy/mapping/split/coverage/freeze change, certificate-state change, or violation of `ECHO-FREE-TIER-001`.
