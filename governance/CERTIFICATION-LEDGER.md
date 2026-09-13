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
| EMP-DATASET-001 | Exact admitted MK1 corpus identity/counts/durations/groups | OPEN | acquired sources + Foundry execution | n/a until produced |
| EMP-DATA-QUALITY-001 | Corpus duplicate/quality/diversity evidence | OPEN | hashes/probes/group/dedup reports | n/a until produced |
| CERT-MK1-DF-CORPUS-001 | Named Foundry corpus/profile manifest | OPEN | DF-G0..DF-G8 + EMP-DATASET-001 + EMP-DATA-QUALITY-001 | any source/asset/policy/mapping/split change |
| CERT-DOC-001 | Global Markdown documentation depth/coverage at prior corpus | INVALIDATED | prior 175-file audit | invalidated when Data Foundry Markdown changed corpus |
| CERT-DOC-002 | Global Markdown documentation depth/coverage including MK1 Data Foundry | CERTIFIED | DOCUMENTATION-STANDARD + COVERAGE + prior audit + Foundry re-audit | audited `.md` corpus materially changes without re-audit |
| EXT-CAMERA-001 | Real camera integration | EXTERNAL_GATE_OPEN | brand/model/audio/RTSP/codec/network/access | closes only with field evidence |
| EMP-MODEL-001 | Model winner | OPEN | MK1 benchmark results on certified Foundry corpus | n/a |
| EMP-DIST-001 | Distance/SNR envelope | OPEN | field tests | n/a |
| EMP-SLO-001 | Final SLOs | OPEN | MK1 runtime/quality evidence | n/a |

## Foundry certificate scope

`CERT-MK1-DF-SPEC-001` certifies that ECHO now has a versioned, testable foundation for source registry, semantic mapping, rights/admission, provenance/hash, grouping/splitting, exact duplicate controls, manifest identity, dataset metadata adapters and related schemas/CLI. GitHub Actions run `34741450390` passed on Python 3.10, 3.11 and 3.12; the 3.11 job ran 23 unit tests successfully.

It does **not** certify final source acquisition, exact corpus counts, audio decoding/resampling, near-duplicate fingerprints, model quality or field performance. Those are intentionally represented by open empirical/corpus nodes rather than inferred from documentation.

## Documentation certificate lineage

`CERT-DOC-001` is an immutable historical certificate over the earlier 175-file Markdown corpus. Once the Data Foundry added substantive Markdown, its current-corpus claim became `INVALIDATED` by design. `CERT-DOC-002` supersedes it after `governance/DOCUMENTATION-AUDIT-2026-09-13-MK1-FOUNDRY.md` reviewed the new corpus.

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
      -> EMP-DATASET-001
      -> EMP-DATA-QUALITY-001
      -> CERT-MK1-DF-CORPUS-001
          -> MK1 replay/audio pipeline
          -> EMP-MODEL-001

DOCUMENTATION-STANDARD
  -> DOCUMENTATION-COVERAGE
      -> DOCUMENTATION-AUDIT-2026-09-13      -> CERT-DOC-001 [historical/INVALIDATED for current corpus]
      -> DOCUMENTATION-AUDIT-2026-09-13-MK1-FOUNDRY -> CERT-DOC-002

EXT-CAMERA-001 -----> real-camera test branch
MK1/test -----------> EMP-DIST-001 / EMP-SLO-001
```

## Invalidation

Un cambio de taxonomy, schema, source contract, Foundry source registry/mapping/admission/split/manifest semantics, model benchmark set, delivery semantics o privacy policy obliga a recalcular versión/hash del artefacto afectado y pasar dependientes a `INVALIDATED` hasta re-auditar.

`CERT-DOC-002` pasa a `INVALIDATED` si se agrega o reemplaza Markdown sustantivo sin revisión de cobertura, si aparece un stub utilizado como input certificado o si el inventario del audit deja de representar el corpus real.

No se usa blockchain: Git + hashes de assets + manifests + CI attestations dan la propiedad requerida sin consenso distribuido.