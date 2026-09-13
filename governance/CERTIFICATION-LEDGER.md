# Certification Ledger

El ledger registra qué evidencia/decisión ha sido certificada y de qué depende. El Git commit que contiene este documento funciona como envelope inmutable de esa versión del ledger.

## Estados

`OPEN` · `CANDIDATE` · `CERTIFIED` · `INVALIDATED` · `EXTERNAL_GATE_OPEN`

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
| CERT-MK1-READY-001 | MK1 replay-build readiness | CERTIFIED | MK0 + DoR | any architecture-changing dependency |
| CERT-MK1-DF-SPEC-001 | MK1 Data Foundry architecture/contracts/policies/core foundation | CERTIFIED | Foundry docs/config/schema/code + CI run 34741450390 | taxonomy, source-registry semantics, mapping, admission/rights, split/manifest semantics or foundation tests |
| CERT-MK1-DF-TOOLCHAIN-001 | Acquisition→intake→probe/admission→review→dedup/split→freeze→benchmark-handoff toolchain | CERTIFIED | code baseline `2c4d4c2...` + CI run 34742947903 + 42-test synthetic E2E suite | Foundry execution semantics/config/schema/probe/dedup/handoff/CI coverage |
| EMP-DATASET-001 | Exact admitted MK1 corpus identity/counts/durations/groups | OPEN | acquired sources + certified Foundry execution | n/a until produced |
| EMP-DATA-QUALITY-001 | Corpus duplicate/quality/diversity evidence | OPEN | real hashes/probes/group/dedup reports | n/a until produced |
| CERT-MK1-DF-CORPUS-001 | Named Foundry corpus/profile manifest | OPEN | DF-G0..DF-G8 on real media + EMP-DATASET-001 + EMP-DATA-QUALITY-001 | any source/asset/policy/mapping/split change |
| CERT-DOC-001 | Global Markdown documentation depth/coverage — historical first audit | INVALIDATED | original audited corpus | superseded when corpus changed |
| CERT-DOC-002 | Documentation depth/coverage including initial MK1 Data Foundry | INVALIDATED | 189-file Foundry audit corpus | superseded by completed toolchain docs/certification |
| CERT-DOC-003 | Documentation depth/coverage including complete MK1 Data Foundry toolchain | CERTIFIED | DOCUMENTATION-STANDARD + COVERAGE + Foundry toolchain audit | audited 197-file `.md` corpus materially changes without re-audit |
| EXT-CAMERA-001 | Real camera integration | EXTERNAL_GATE_OPEN | brand/model/audio/RTSP/codec/network/access | closes only with field evidence |
| EMP-MODEL-001 | Model winner | OPEN | A/B/C benchmark results on certified Foundry corpus | n/a |
| EMP-THRESH-001 | Per-class model/EventEngine thresholds | OPEN | validation + streaming replay evidence | n/a |
| EMP-DIST-001 | Distance/SNR envelope | OPEN | authorized field tests | n/a |
| EMP-CAP-001 | Multi-source capacity envelope | OPEN | load/soak on target hardware | n/a |
| EMP-SLO-001 | Final MK1/MK2 SLO evidence | OPEN | runtime/quality/field evidence | n/a |

## Foundry certification scope

`CERT-MK1-DF-SPEC-001` certifies the versioned architecture/contracts/policy foundation.

`CERT-MK1-DF-TOOLCHAIN-001` certifies the executable engineering chain through DF-G8: acquisition registry/checksum verification, source adapters/intake, technical media probing, SHA-256, rights admission, semantic mapping/manual review, group and duplicate/label-conflict guards, deterministic split policy, freeze reports/manifests and benchmark-facing frozen-bundle validation. GitHub Actions run `34742947903` passed on Python 3.10, 3.11 and 3.12; the Python 3.11 job ran 42 tests successfully.

Neither certificate fabricates real-corpus facts. Exact real counts/diversity/license distribution/duplicates and target coverage remain outputs of `EMP-DATASET-001` and `EMP-DATA-QUALITY-001`, and only then can `CERT-MK1-DF-CORPUS-001` close.

## Documentation certificate lineage

```text
CERT-DOC-001  historical; invalidated for later corpus
CERT-DOC-002  historical; invalidated/superseded after toolchain documentation expansion
CERT-DOC-003  current; certifies 197-file Markdown corpus
```

Historical audits remain evidence for the exact repository states they covered; invalidation means only that they no longer describe the current corpus.

## Dependency DAG

```text
CERT-ECHO-000
  -> CERT-MK0-001
      -> CERT-MK0-003 -> CERT-MK0-010
      -> CERT-MK0-002 -> CERT-MK0-011
      -> CERT-MK0-004 -> CERT-MK0-005
      -> CERT-MK0-006 -> CERT-MK0-007 -> CERT-MK0-008 -> CERT-MK0-009
      -> CERT-MK0-012

CERT-MK0-002..012
  -> CERT-MK0-013
  -> CERT-MK1-READY-001

CERT-MK1-READY-001
  -> CERT-MK1-DF-SPEC-001
      -> CERT-MK1-DF-TOOLCHAIN-001
          -> EXEC-DATA-001 [real source-media execution]
              -> EMP-DATASET-001
              -> EMP-DATA-QUALITY-001
              -> CERT-MK1-DF-CORPUS-001
                  -> MK1 replay/audio pipeline
                  -> A/B/C benchmark
                      -> EMP-MODEL-001
                      -> EMP-THRESH-001

DOCUMENTATION-STANDARD
  -> DOCUMENTATION-COVERAGE
      -> original audit -> CERT-DOC-001 [historical]
      -> MK1 Foundry audit -> CERT-DOC-002 [historical]
      -> MK1 Foundry Toolchain audit -> CERT-DOC-003 [current]

EXT-CAMERA-001 -----> real-camera test branch -> EMP-DIST-001
MK1 load/soak ------> EMP-CAP-001
MK1 quality/runtime -> EMP-SLO-001
```

## Invalidation

Un cambio de taxonomy, schema, source/audio contract, Foundry source/acquisition registry semantics, mapping/admission/review/probe/dedup/split/manifest/handoff semantics, model benchmark set, delivery semantics o privacy policy obliga a recalcular versión/hash del artefacto afectado y pasar dependientes a `INVALIDATED` hasta re-auditar.

`CERT-DOC-003` pasa a `INVALIDATED` si se agrega o reemplaza Markdown sustantivo sin revisión de cobertura, aparece un stub utilizado como input certificado o el inventario de 197 archivos deja de representar el corpus real.

No se usa blockchain: Git + hashes de assets + manifests + CI attestations dan la propiedad requerida sin consenso distribuido.
