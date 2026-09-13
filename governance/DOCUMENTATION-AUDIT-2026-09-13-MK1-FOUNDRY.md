# Documentation Audit — MK1 Data Foundry Extension — 2026-09-13

**Status:** `PASS`  
**Successor certificate:** `CERT-DOC-002`  
**Supersedes for current corpus:** `CERT-DOC-001`

## 1. Trigger

The previous global Markdown audit certified a 175-file corpus. MK1 Data Foundry construction added substantive design/build/test documentation, which intentionally triggered `CERT-DOC-001` invalidation under its own coverage rule.

This audit reviews the new Markdown and confirms that the previous audited corpus was not weakened by the Foundry changes.

## 2. Corpus accounting

```text
previous audited Markdown corpus                     175
new MK1/build/data-foundry Markdown artifacts        +12
new MK1/test Data Foundry evidence                    +1
pre-audit current corpus                              188
this audit document                                   +1
final Markdown corpus                                 189
```

Existing files updated in place (`CURRENT-STATE.md`, `MK1/README.md`, `MK1/build/README.md`, `MK1/mining-site/DATASET-SELECTION.md`, certification ledger) do not change the file count; their new content was reviewed as part of this audit.

## 3. New Foundry artifacts reviewed

### MK1/build/data-foundry — 12/12 PASS

- [x] `README.md` — responsibility, data zones, source roles, gaps, outputs and stop-line conditions.
- [x] `FOUNDRY-ARCHITECTURE.md` — adapter/gating/manifest architecture, boundaries and reproducibility identity.
- [x] `SOURCE-CATALOG.md` — source-by-source evidence, rights posture, semantic value and explicit target gaps.
- [x] `LABEL-MAPPING-V1.md` — relation types, mappings, manual review, forbidden broad-label coercions.
- [x] `ADMISSION-POLICY.md` — provenance, rights, quarantine/rejection, profile separation and invalidation.
- [x] `MANIFEST-CONTRACT.md` — asset/dataset/split identities and canonical serialization.
- [x] `SPLIT-DEDUP-POLICY.md` — group-aware separation, source-specific grouping, duplicates/augmentation/holdout.
- [x] `HARD-NEGATIVE-CATALOG.md` — target-specific confuser families, mining loop and leakage controls.
- [x] `FIELD-HOLDOUT.md` — field separation, capture metadata, privacy, external gate and evidence role.
- [x] `RUNBOOK.md` — executable acquisition-to-freeze procedure, required reports and stop conditions.
- [x] `FOUNDRY-GATES.md` — DF-G0..DF-G8, corpus certificate path and empirical/open boundaries.
- [x] `WEB-EVIDENCE-2026-09-13.md` — source-level evidence/provenance and epistemic classification.

### MK1/test — 1/1 PASS

- [x] `DATA-FOUNDRY-FOUNDATION.md` — exact commits, workflow/run identity, Python matrix, 23-test evidence, scope and non-claims.

## 4. Reconstructibility check

A reader opening the Foundry subtree without the original chat can determine:

```text
why the Foundry exists
which source families are currently considered
what each source contributes and what it cannot prove
which rights profiles exist
how upstream labels map or fail to map to ECHO
how assets are admitted/quarantined/rejected
how groups/splits prevent leakage
what hashes/manifests identify a corpus
what remains empirical
what the CI actually validated
what must happen before model training
what upstream changes invalidate evidence
```

Result: `PASS`.

## 5. Stub check

- substantive Foundry documents consisting only of TODO/questions: **0**;
- new authoritative status-only documents without evidence contract: **0**;
- target/source headline facts presented as admitted-corpus results: **0**;
- empirical counts fabricated before corpus execution: **0**.

## 6. Epistemic discipline

The extension preserves the distinction between:

- `FACT/EVIDENCE`: source release facts and CI results;
- `DECISION`: taxonomy/mapping/admission/split/manifest policy;
- `HYPOTHESIS/OPEN`: data sufficiency and future field behavior;
- `EMPIRICAL`: exact admitted counts, duplicates, source diversity and benchmark results.

In particular, `FIRE_ALARM` and `TIRE_SQUEAL` data gaps are retained as gaps instead of being hidden through broad-label remapping.

## 7. Code/config evidence relationship

Markdown is paired with machine-readable artifacts under `configs/data_foundry/` and `schemas/data_foundry/`, implementation under `src/echo/data_foundry/`, tests under `tests/data_foundry/`, and CI workflow `.github/workflows/mk1-data-foundry-ci.yml`.

GitHub Actions run `34741450390` completed successfully for Python 3.10, 3.11 and 3.12. This supports the foundation certificate but does not turn corpus-level open nodes into certified results.

## 8. Certification result

`CERT-DOC-001`: historical certificate remains evidence of the former corpus, but its **current-corpus status is INVALIDATED** after Foundry Markdown expansion.

`CERT-DOC-002`: `CERTIFIED` for the 189-file Markdown corpus represented by this audit and the commit containing it.

## 9. Future invalidation

`CERT-DOC-002` invalidates when substantive Markdown is added/replaced without a coverage review, when an authoritative artifact regresses to a stub, or when the recorded inventory no longer matches the repository corpus.