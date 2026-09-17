# Estado actual de ECHO

**Fecha de corte:** 2026-09-16  
**Status:** `ACTIVE_SOURCE_OF_TRUTH`  
**Global execution invariant:** `ECHO-FREE-TIER-001`  
**Documentation certificate:** `CERT-DOC-015`

## 1. Promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

La promesa permanece inmutable. Cámaras, RTSP/ONVIF, MQTT, dashboards, persistencia y alertas son soporte; no redefinen el core acústico.

## 2. MK1 critical path

```text
release-safe corpus
→ coverage PASS / gap_codes=[]
→ freeze #1
→ freeze #2 clean
→ reproducibility PASS
→ pre-certificate readiness with exactly CORPUS_CERTIFICATE_NOT_CERTIFIED
→ CERT-MK1-DF-CORPUS-001
→ final readiness READY / modeling_allowed=true
→ Benchmark A/B/C
→ model winner
→ Event Engine → Edge Agent → MQTT/replay → real camera
```

## 3. Current state

```text
MK0                               CERTIFIED
MK1 spec/design/architecture      CLOSED_FOR_BUILD
Data Foundry spec                 CERTIFIED
SONYC materialization             CERTIFIED / scoped
Foundry toolchain                 TOOLCHAIN-005 CERTIFIED
Corpus certificate handoff        HANDOFF-001 CERTIFIED
Global acoustic grouping          PASS
Global dedup                      PASS
Recording-family audit            PASS
Split integrity                   PASS
Split quarantine                  0 assets
Coverage                          FAIL / 16 empirical gaps
Freeze #1                         FAIL / coverage only
Freeze #2                         FAIL / coverage only
Reproducibility                   FAIL / freeze not eligible
Corpus readiness                  BLOCKED_FAIL_CLOSED
CERT-MK1-DF-CORPUS-001            OPEN
modeling_allowed = false
Benchmark A/B/C                   LOCKED
MK2                               GATED_BY_MK1
```

No paid fallback, label coercion, source-family inflation, split shopping or lowered quality floor is authorized.

## 4. Certificate lineage

```text
CERT-MK1-DF-SPEC-001              = CERTIFIED
CERT-MK1-DF-TOOLCHAIN-001..003    = historical
CERT-MK1-DF-TOOLCHAIN-004         = INVALIDATED
CERT-MK1-DF-TOOLCHAIN-005         = CERTIFIED
CERT-MK1-DF-SONYC-001             = CERTIFIED / scoped
CERT-MK1-DF-HANDOFF-001           = CERTIFIED
CERT-MK1-DF-CORPUS-001            = OPEN

CERT-DOC-001..014                 = historical / invalidated
CERT-DOC-015                      = CERTIFIED / current
```

TOOLCHAIN-005 is scoped to the proven atomic evidence/readiness-v2 implementation. HANDOFF-001 separately governs conditional certificate issuance.

## 5. Canonical semantic corpus truth

```text
assets                              1141
canonical fingerprints              1141 / 1141
missing fingerprints                0
ledger blockers                     0
recording families                  1075
split quarantine                    0
semantic ledger sha256              cec960c16c2dbbd4fed8f4ad4e473e76a1eb7c101be8975d055907b796d81ed1
coverage ledger sha256              93be3dceee44df0dfc51ab38c078f1e1e6587ba91e4fbbc53c3b65065e58bfa8
readiness semantic identity         4297dc73cae803c3b8b4e92c767844d04f598be93abe6ca560f17e7fc4a11405
```

`baseline_commit` and generated-summary byte hashes remain **execution provenance**. Readiness v2 binds semantic ledger content, coverage policy and closure evidence instead.

## 6. Atomic corpus + certificate pipeline

There is one durable writer:

```text
governed source evidence
→ canonical ledger
→ grouping
→ dedup / family / split
→ coverage
→ freeze #1 / freeze #2
→ reproducibility
→ pre-certificate readiness
→ conditional certificate emitter
→ final readiness
→ one atomic durable commit
```

The orchestrator rebuilds the cascade twice, byte-compares it, refuses persistence if `main` moved and never relies on repository-token push recursion.

`CERT-MK1-DF-HANDOFF-001` freezes the transition rule. A corpus certificate may be emitted only when pre-certificate readiness has exactly:

```text
eligible_for_certificate_review = true
status = BLOCKED
modeling_allowed = false
gap_codes = [CORPUS_CERTIFICATE_NOT_CERTIFIED]
```

If any other gap exists, issuance is a no-op. An existing stale/invalid corpus certificate is never overwritten silently.

## 7. Structural closure

```text
candidate near-duplicate threshold            0.02
confirmed grouping threshold                  0.002
max decoded-sample relative delta              0.01
screening candidates                           855
screening candidates cross-group               849
confirmed relations                              2
confirmed cross-group conflicts                   0
length-rejected candidates                     835
exact media duplicate groups                     0
exact canonical-PCM duplicate groups             0

global-dedup-audit.json       PASS
group/family audit            PASS
split-integrity.json          PASS
```

Screening evidence is never automatic acoustic identity. Review-only edges never union recording components.

## 8. Current coverage

```text
BACKGROUND      428 assets / 385 groups / 4 sources                         PASS
FIRE_ALARM       19 assets / 16 groups / 3 sources / 460.864037 s           FAIL
GLASS_SHATTER   303 assets / 287 groups / 4 sources / 1244.131193 s         FAIL concentration
SIREN           169 assets / 169 groups                                      PASS
TIRE_SQUEAL      14 assets / 10 groups / 2 sources / 344.600098 s           FAIL
VEHICLE_HORN    235 assets / 235 groups                                      PASS
```

FIRE hard negatives: 202/202/4 PASS. GLASS hard negatives: 440/410/2 PASS. TIRE hard negatives: 25/12/2 PASS. Asset-quality stop lines remain zero.

## 9. Remaining 16 coverage gaps

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

Minimum empirical deficits remain FIRE +31 assets/+9 groups, TIRE +36 assets/+15 groups and GLASS +47 surviving non-Freesound positives if Freesound remains at 280.

## 10. Current readiness

```text
schema = echo.corpus-closure-readiness.v2
readiness_id = EMP-MK1-CORPUS-READINESS-001
status = BLOCKED
eligible_for_certificate_review = false
modeling_allowed = false
CERT-MK1-DF-CORPUS-001 = OPEN
next_authorized_stage = CORPUS_FOUNDRY_CLOSURE
```

Current readiness gaps remain certificate + coverage + FIRE/TIRE + freeze/repro blockers. No structural dedup/group/split blocker remains.

## 11. Immediate execution priority

Infrastructure polishing stops unless a blocker proves it necessary. Work now moves to release-safe acquisition for FIRE_ALARM, TIRE_SQUEAL and non-Freesound GLASS_SHATTER. Every new asset must survive rights, exact semantics, probe, canonical fingerprint, grouping, dedup and deterministic split assignment.

When coverage reaches PASS, the already-wired handoff executes:

```text
coverage PASS
→ freeze/repro PASS
→ certificate emitter legal
→ CERT-MK1-DF-CORPUS-001
→ modeling_allowed=true
→ Benchmark A/B/C
```

## 12. Release law

```text
NO CERT-MK1-DF-CORPUS-001
=
NO Benchmark A/B/C
NO YAMNet/PANNs/CNN model work
NO threshold calibration
NO replay progression
NO real camera progression
```

## 13. Documentation state

```text
governance/DOCUMENTATION-AUDIT-2026-09-16-CORPUS-HANDOFF-015.md
CERT-DOC-015                   = CERTIFIED / current
Markdown corpus                = 221 files
```

## 14. Invalidation

Material changes to promise, taxonomy, rights/mapping/fingerprint/grouping/dedup/split/coverage/freeze/reproducibility semantics, readiness identity, Toolchain-005, Handoff-001, model-entry wiring, certificate state or `ECHO-FREE-TIER-001` require dependency review and selective recertification. Execution provenance churn alone does not redefine an unchanged semantic corpus.
