# MK1 Data Foundry — Execution Runbook

**Status:** `READY_FOR_LOCAL_EXECUTION`

## 1. Objective

Execute corpus construction reproducibly without hand-picking files. This runbook is the operational bridge from source releases to frozen manifests.

## 2. Preconditions

- source registry and label mapping versions selected;
- intended profile selected (`release_safe`, `research_extended`, or `field_holdout`);
- upstream release acquired from its canonical source by an authorized operator;
- local raw release treated read-only;
- sufficient disk space for source audio plus staging/report artifacts;
- no credentials embedded in config/manifests.

## 3. Recommended workspace

```text
workspace/
  data/external/<source-release>/
  data/staging/<run-id>/
  data/quarantine/<run-id>/
  data/manifests/
  data/reports/<run-id>/
```

The repository contains policies/code, not the raw corpora.

## 4. Foundry sequence

### Step A — verify source release

Record source ID, release, canonical URL/DOI, upstream checksums where provided and acquisition timestamp. Never merge files from multiple releases under one source identity.

### Step B — adapter extraction

Run the dataset adapter against source metadata. Adapter output is `RawAssetCandidate`; inspect source count and required-column errors before continuing.

### Step C — rights/provenance classification

Normalize license terms and assign use decision. Unknown/custom terms go to quarantine. Generate per-source decision counts.

### Step D — semantic mapping

Apply `label_mapping.v1`. `BROADER`/`AMBIGUOUS` positive candidates enter manual review instead of automatic target admission. Retain all original labels.

### Step E — content identity

Resolve local audio file and compute SHA-256/byte size. A missing/unreadable file is rejected from the frozen manifest and reported.

### Step F — audio quality probe

When the decoder/probe increment is enabled, record duration/sample-rate/channels and invalid/corrupt status. Never resample or overwrite raw source audio in place.

### Step G — duplicate/group audit

Cluster exact hashes; check label conflicts; establish conservative recording groups. Record unresolved group identity as a blocking issue for protected evaluation use.

### Step H — split planning

Apply explicit benchmark split profile to groups. Preserve locked field holdout. Audit zero cross-split group/hash overlap.

### Step I — manifest freeze

Sort records canonically, emit JSONL and dataset/split manifests, calculate SHA-256 digests and write coverage/license/quarantine reports.

### Step J — certification handoff

Record manifest identities in `MK1/mining-site/DATASET-SELECTION.md` and the build manifest. Only then can the model benchmark claim a fixed data identity.

## 5. Suggested CLI progression

Current stdlib Foundry CLI supports integrity/policy building blocks; source-adapter orchestration is expanded incrementally.

```text
python -m echo.data_foundry.cli validate-source-registry configs/data_foundry/source_registry.v1.json
python -m echo.data_foundry.cli hash-file <local-audio-file>
python -m echo.data_foundry.cli digest-json configs/data_foundry/label_mapping.v1.json
python -m echo.data_foundry.cli plan-split <group-id> --seed <seed> --train <ratio> --validation <ratio> --test <ratio>
```

No split ratio is implied by this documentation; benchmark configuration supplies it explicitly after corpus composition is known.

## 6. Required generated reports

For each run:

```text
run identity/config hashes
source counts
admitted/quarantined/rejected counts + reason
license distribution
mapping-relation distribution
per-target independent groups / assets / duration
hard-negative coverage
split counts and group overlap audit
exact duplicate clusters and label conflicts
missing/corrupt-file report
known target-coverage gaps
```

## 7. Re-run semantics

Running the same code/config/source bytes should reproduce the same candidate identities, group assignments and manifest digest. Timestamp/report metadata can differ but must not influence canonical asset-manifest hashing.

## 8. Stop conditions

Do not proceed to model training when:

- source release/version cannot be established;
- protected split leakage exists;
- license policy has unresolved assets accidentally marked admitted;
- exact duplicate label conflicts remain unresolved in protected evaluation data;
- a target is represented primarily by broad/ambiguous labels without review;
- field holdout has been touched by training/calibration logic.

## 9. What this runbook does not do

It does not download restricted/non-approved media automatically, choose a model, set event thresholds, claim target sufficiency, or certify real-camera performance. Those are separate evidence gates.