# Certification Ledger

**Status:** `ACTIVE_SOURCE_OF_CERTIFICATION_TRUTH`  
**Global execution ancestor:** `ECHO-FREE-TIER-001`  
**Documentation ancestor:** `CERT-DOC-004`

El ledger registra qué evidencia/decisión ha sido certificada, de qué depende, qué no certifica y qué la invalida. El Git commit que contiene este documento funciona como envelope inmutable de esa versión del ledger.

## Estados

`OPEN` · `CANDIDATE` · `CERTIFIED` · `INVALIDATED` · `EXTERNAL_GATE_OPEN`

`CERTIFIED` siempre está acotado por scope. Un certificado documental no fabrica evidencia empírica; un CI verde no compensa documentación contradictoria; y ningún certificado puede depender de una ruta que viole `ECHO-FREE-TIER-001`.

## Certificates and empirical outputs

| Certificate ID | Artefacto/claim | Estado | Inputs principales | Invalida si cambia |
|---|---|---|---|---|
| CERT-ECHO-000 | Promesa inmutable | CERTIFIED | PROJECT-CHARTER | promesa del propietario |
| CERT-MK0-001 | Boundary: eventos acústicos observables | CERTIFIED | charter + anti-scope | promise/boundary |
| CERT-MK0-002 | Landscape de modelos | CERTIFIED | TensorFlow, PANNs, AST, HTS-AT, PaSST, BEATs | source/version material |
| CERT-MK0-003 | Landscape de datasets | CERTIFIED | AudioSet, FSD50K, SONYC, ESC-50, DCASE | license/release facts |
| CERT-MK0-004 | RTSP source abstraction | CERTIFIED | ONVIF + FFmpeg/GStreamer docs | source contract |
| CERT-MK0-005 | FFmpeg baseline MK1 | CERTIFIED | FFmpeg docs + codec abstraction | incompatible required codec |
| CERT-MK0-006 | Multi-label inference contract | CERTIFIED | YAMNet + SONYC + polyphonic SED | taxonomy semantics |
| CERT-MK0-007 | Event lifecycle separation | CERTIFIED | SED/event-system design | event contract |
| CERT-MK0-008 | MQTT/Mosquitto MK1 bus | CERTIFIED | OASIS MQTT + Mosquitto + Frigate precedent | delivery requirements |
| CERT-MK0-009 | QoS1 + idempotency | CERTIFIED | MQTT 5.0 semantics | delivery semantics |
| CERT-MK0-010 | MK1 target taxonomy v1 | CERTIFIED | AudioSet evidence + domain relevance | label/data evidence |
| CERT-MK0-011 | Benchmark protocol v1 | CERTIFIED | model/data/metrics research | target taxonomy/model set |
| CERT-MK0-012 | Privacy-by-design requirement | CERTIFIED | project policy + Peru normative evidence | jurisdiction/policy |
| CERT-MK0-013 | MK0 research gate | CERTIFIED | CERT-MK0-001..012 | any dependency above |
| CERT-MK1-READY-001 | MK1 replay-build readiness | CERTIFIED | MK0 + DoR | architecture-changing dependency |
| CERT-MK1-DF-SPEC-001 | MK1 Data Foundry architecture/contracts/policies/core foundation | CERTIFIED | Foundry docs/config/schema/code + CI evidence | taxonomy, source-registry semantics, mapping, admission/rights, split/manifest semantics or foundation tests |
| CERT-MK1-DF-TOOLCHAIN-001 | Historical Data Foundry toolchain baseline `2c4d4c2...` | INVALIDATED | CI run 34742947903 + 42-test suite | superseded by material current-baseline changes and CERT-MK1-DF-TOOLCHAIN-002 |
| CERT-MK1-DF-TOOLCHAIN-002 | Current acquisition→intake→probe/admission→review→coverage/dedup/split→freeze→benchmark-handoff toolchain | CERTIFIED | baseline `be75a432...` + CI run 34800084225 + 67-test Python 3.11 evidence + green 3.10/3.12 matrix | certified code/config/schema/test/workflow surface or zero-cost execution contract |
| EMP-DATASET-001 | Exact admitted MK1 corpus identity/counts/durations/groups | OPEN | real admitted release-safe assets + closure execution | n/a until produced |
| EMP-DATA-QUALITY-001 | Corpus duplicate/quality/diversity evidence | OPEN | real hashes/probes/group/dedup/near-dup reports | n/a until produced |
| CERT-MK1-DF-CORPUS-001 | Named release-safe Foundry corpus/profile manifest | OPEN | DF-G0..DF-G8 + hard-negative + near-dup + reproducibility + free-tier PASS + EMP-DATASET-001 + EMP-DATA-QUALITY-001 | any source/asset/policy/mapping/group/split/fingerprint change |
| CERT-DOC-001 | Global Markdown documentation depth/coverage — first historical audit | INVALIDATED | original audited corpus | superseded when corpus changed |
| CERT-DOC-002 | Documentation including initial MK1 Data Foundry | INVALIDATED | 189-file Foundry audit corpus | superseded by later toolchain docs |
| CERT-DOC-003 | Documentation including completed original MK1 Foundry toolchain | INVALIDATED | 197-file corpus at commit `7ef9c1d...` | superseded after corpus-closure/free-tier documentation expansion |
| CERT-DOC-004 | Current documentation depth/reconstructibility/coherence for corpus-closure baseline | CERTIFIED | DOCUMENTATION-STANDARD + DOCUMENTATION-COVERAGE + corpus-closure audit + 206-file Markdown corpus | substantive Markdown/policy truth changes without re-audit, contradiction, authoritative stub |
| EXT-CAMERA-001 | Real camera integration | EXTERNAL_GATE_OPEN | brand/model/audio/RTSP/codec/network/access/site authorization | closes only with field evidence |
| EMP-MODEL-001 | Model winner | OPEN | A/B/C benchmark results on certified Foundry corpus | n/a |
| EMP-THRESH-001 | Per-class classifier/Event Engine thresholds | OPEN | validation + streaming replay evidence | n/a |
| EMP-DIST-001 | Distance/SNR envelope | OPEN | authorized field tests | n/a |
| EMP-CAP-001 | Multi-source capacity envelope | OPEN | load/soak on target hardware | n/a |
| EMP-SLO-001 | Final MK1/MK2 SLO evidence | OPEN | runtime/quality/field evidence | n/a |

## Universal certificate ancestors

Every new certificate must satisfy the applicable chain:

```text
CERT-ECHO-000 / scope boundary
        +
current documentation certificate
        +
ECHO-FREE-TIER-001 = PASS
        +
required upstream technical/empirical certificates
        ↓
certificate eligibility
```

A documentation certificate certifies reconstructibility/coherence for its scope; it does not turn an `OPEN` empirical result into evidence. Likewise, strong empirical results cannot be promoted while governing documentation is stale or contradictory.

## Current Foundry certification scope

`CERT-MK1-DF-SPEC-001` certifies the versioned architecture/contracts/policy foundation.

`CERT-MK1-DF-TOOLCHAIN-002` supersedes the original toolchain certificate for the current engineering baseline. GitHub Actions run `34800084225` checked out exact SHA `be75a4323ec67f7c9528cbdbf6a06a8524494501` and passed Python 3.10, 3.11 and 3.12. The Python 3.11 job executed 67 tests successfully, including source/publisher policy, release-safe coverage enforcement, rights/semantic gates, field-holdout protection, hard-negative requirements, duplicate/group leakage, deterministic splits and synthetic freeze/handoff coverage.

The deep-research closure pass intentionally leaves stricter final-corpus nodes open:

```text
canonical global admitted asset ledger
hard-negative materialization/admission evidence
cross-format/transcode-aware near-duplicate policy + fixture validation
global recording-family/source-independence audit
real class/split/source coverage PASS
freeze validation
second clean freeze reproducibility
```

Therefore `CERT-MK1-DF-CORPUS-001` remains `OPEN` until actual evidence closes them. No real counts/diversity/license distribution/duplicate absence/model metric is inferred from the toolchain certificate.

## Documentation certificate lineage

```text
CERT-DOC-001  historical -> INVALIDATED for later corpus
CERT-DOC-002  historical -> INVALIDATED/SUPERSEDED
CERT-DOC-003  historical -> INVALIDATED for current HEAD; certified 197-file corpus at its own baseline
CERT-DOC-004  current    -> CERTIFIED; 206-file Markdown corpus + coherence audit
```

`CERT-DOC-004` incorporates the corpus-closure research and zero-cost governance delta. The audit corrected, before promotion, two material contradictions: old 120 GiB/self-hosted materialization guidance versus `ECHO-FREE-TIER-001`, and stale current-state language that hid newly identified closure-critical implementation/integration nodes.

Historical audits remain immutable evidence for the repository states they covered.

## Dependency DAG

```text
CERT-ECHO-000
  + CERT-DOC-004
  + ECHO-FREE-TIER-001
          |
          v
CERT-MK0-001..012
          |
          v
CERT-MK0-013
          |
          v
CERT-MK1-READY-001
          |
          v
CERT-MK1-DF-SPEC-001
          |
          v
CERT-MK1-DF-TOOLCHAIN-002
          |
          v
MK1 CORPUS FOUNDRY CLOSURE / EXEC-DATA-001
       |                  |
       v                  v
EMP-DATASET-001    EMP-DATA-QUALITY-001
       \                  /
        \                /
         v              v
        CERT-MK1-DF-CORPUS-001
                 |
                 +----------------------+
                 |                      |
                 v                      v
        MK1 replay/audio          A/B/C benchmark
                                        |
                                        v
                                EMP-MODEL-001
                                        |
                                        v
                                EMP-THRESH-001

EXT-CAMERA-001 -----------------> real-camera test branch -> EMP-DIST-001
MK1 load/soak ------------------> EMP-CAP-001
MK1 quality/runtime/field ------> EMP-SLO-001
```

Documentation lineage is transversal rather than a seventh MK phase:

```text
DOCUMENTATION-STANDARD
  -> DOCUMENTATION-COVERAGE
      -> CERT-DOC-001 [historical]
      -> CERT-DOC-002 [historical]
      -> CERT-DOC-003 [historical]
      -> CERT-DOC-004 [current]
```

## Invalidation

A material change to promise, taxonomy, schema, source/audio/event contract, source/acquisition registry semantics, mapping/admission/review/probe/coverage/dedup/split/manifest/handoff semantics, benchmark set, delivery semantics, privacy policy, zero-cost execution boundary or governing documentation requires dependency review and selective invalidation/re-certification.

`CERT-MK1-DF-TOOLCHAIN-002` becomes invalid if its certified code/config/schema/test/workflow surface changes materially without rerun.

`CERT-DOC-004` becomes invalid/stale for current HEAD if substantive Markdown or policy truth changes without review, a certified input regresses into a stub, prose contradicts machine-readable authority, or the 206-file inventory no longer represents the documentation corpus.

No blockchain is used: Git history + content hashes + manifests + CI evidence provide the required traceability without distributed consensus.