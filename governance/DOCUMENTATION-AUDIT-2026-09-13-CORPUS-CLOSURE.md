# Documentation Audit — Corpus Foundry Closure Baseline — 2026-09-13

**Certificate:** `CERT-DOC-004`  
**Status:** `CERTIFIED`  
**Supersedes for current HEAD:** `CERT-DOC-003`  
**Previous documentation certificate baseline:** `7ef9c1d52b12396e6e73f00f0a3a442d49061fe3`  
**Previous certified Markdown corpus:** 197 files  
**Current certified Markdown corpus:** 206 files  
**Global execution invariant:** `ECHO-FREE-TIER-001`

## 1. Purpose

This audit re-establishes documentation depth, reconstructibility and cross-document coherence after the MK1 Data Foundry moved from its original toolchain-complete state into active real-data materialization and Corpus Foundry Closure.

The trigger is substantive: new research, new data-solidity rules, source/materialization evidence, a global zero-cost execution boundary and a stricter corpus-closure DAG were added after `CERT-DOC-003`. Under ECHO's own invalidation rules, the earlier certificate cannot silently stretch to cover those artifacts.

This audit therefore answers:

```text
Can another engineer/agent reconstruct current ECHO truth from the repository alone?
Do current authoritative documents agree with each other?
Are empirical/open nodes still represented honestly?
Does the documented execution path obey ECHO-FREE-TIER-001?
Is the current Foundry engineering certificate tied to current test evidence?
```

## 2. Scope and non-scope

### In scope

- documentation added after `CERT-DOC-003`;
- material rewrites affecting Corpus Foundry execution truth;
- consistency among charter, current state, certification ledger/DAG, free-tier governance and Foundry closure documents;
- alignment between current documentation claims and the current certified Foundry engineering evidence;
- documentation-to-machine-policy consistency where directly inspectable;
- explicit visibility of remaining open corpus/model/field nodes.

### Not certified by this audit

`CERT-DOC-004` does **not** certify:

```text
final admitted corpus counts or diversity
absence of real-media near duplicates
final hard-negative sufficiency
CERT-MK1-DF-CORPUS-001
model winner / F1 / PR-AUC
production thresholds
latency/capacity envelope
camera/field performance
MK1 end-to-end completion
```

Those remain technical/empirical claims with their own evidence ancestors.

## 3. Evidence and authority reviewed

Primary repository authorities reviewed in this pass:

```text
PROJECT-CHARTER.md
CURRENT-STATE.md
governance/DOCUMENTATION-STANDARD.md
governance/DOCUMENTATION-COVERAGE.md
governance/CERTIFICATION-DAG.md
governance/CERTIFICATION-LEDGER.md
governance/FREE-TIER-BOUNDARY.md
MK1/build/data-foundry/README.md
MK1/build/data-foundry/FOUNDRY-GATES.md
MK1/build/data-foundry/CORPUS-SOLIDITY-GATE.md
MK1/build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md
MK1/build/data-foundry/DATASET-SOURCE-CERTIFICATION.md
MK1/build/data-foundry/MATERIALIZATION.md
MK1/mining-site/CORPUS-CLOSURE-DEEP-RESEARCH-2026-09-13.md
MK1/mining-site/README.md
MK1/quarries/Q-FIRE-ALARM-TIRE-SQUEAL-GAPS.md
MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-002.md
```

Machine/check evidence reviewed for documentation coherence:

```text
configs/data_foundry/free_tier_boundary.v1.json
configs/data_foundry/coverage_policy.v1.json
configs/data_foundry/dataset_certification.v1.json
configs/data_foundry/hard_negative_mapping.v1.json
.github/workflows/mk1-data-foundry-ci.yml
GitHub Actions run 34800084225
scripts/check_free_tier_boundary.py
scripts/check_documentation_governance.py
.github/workflows/documentation-governance.yml
```

## 4. Corpus accounting

`CERT-DOC-003` certified 197 Markdown files.

Seven substantive Markdown artifacts were added before this governance pass:

```text
+ MK1/build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md
+ MK1/build/data-foundry/CORPUS-SOLIDITY-GATE.md
+ MK1/build/data-foundry/DATASET-SOURCE-CERTIFICATION.md
+ MK1/build/data-foundry/MATERIALIZATION.md
+ MK1/mining-site/CORPUS-CLOSURE-DEEP-RESEARCH-2026-09-13.md
+ MK1/quarries/Q-FIRE-ALARM-TIRE-SQUEAL-GAPS.md
+ governance/FREE-TIER-BOUNDARY.md
```

This governance pass adds:

```text
+ MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-002.md
+ governance/DOCUMENTATION-AUDIT-2026-09-13-CORPUS-CLOSURE.md
```

Therefore:

```text
197 + 7 + 1 + 1 = 206 Markdown files
```

Existing Markdown rewritten in place does not change the count.

## 5. Reconstructibility review of new artifacts

### Corpus Foundry Closure Plan

`MK1/build/data-foundry/CORPUS-FOUNDRY-CLOSURE-PLAN.md` defines the closure DAG, gate contracts, near-duplicate hardening requirement, hard-negative evidence requirement, reproducibility sub-gate, final certificate predicate, execution order and post-corpus path.

Result: `PASS`.

It correctly prevents model benchmark promotion until the corpus certificate closes.

### Corpus Solidity Gate

`MK1/build/data-foundry/CORPUS-SOLIDITY-GATE.md` records class/group/source/duration/split/background/hard-negative engineering floors and explicitly states that those floors do not guarantee model performance.

Result: `PASS`.

### Dataset Source Certification

`MK1/build/data-foundry/DATASET-SOURCE-CERTIFICATION.md` distinguishes source/release identity, publisher evidence, rights posture, semantic relevance and final per-asset corpus admission. It records conditional/denied/reference-only sources without laundering those states into release-safe admission.

Result: `PASS`.

### Dataset Materialization

`MK1/build/data-foundry/MATERIALIZATION.md` now defines bounded zero-cost execution, durable evidence versus transient raw bytes, source-specific execution posture and the full corpus admission stop line.

Result after coherence correction: `PASS`.

### Deep Research Synthesis

`MK1/mining-site/CORPUS-CLOSURE-DEEP-RESEARCH-2026-09-13.md` separates `FACT/EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `DECISION` and `TARGET`, records primary evidence and derives the exact final closure requirements without declaring unrun empirical results.

Result: `PASS`.

### FIRE_ALARM / TIRE_SQUEAL Quarry

`MK1/quarries/Q-FIRE-ALARM-TIRE-SQUEAL-GAPS.md` preserves the research-workstream chain from exact-label source discovery through rights/semantic review to empirical closure conditions and explicitly refuses broad-label coercion.

Result: `PASS`.

### Free-tier governance

`governance/FREE-TIER-BOUNDARY.md` freezes zero-cost execution as a project-wide ancestor policy. It prevents paid capacity, automatic overage and quality reduction from becoming silent fallbacks.

Result: `PASS`.

### Toolchain recertification

`MK1/test/DATA-FOUNDRY-TOOLCHAIN-RECERTIFICATION-002.md` binds current engineering certification to exact baseline `be75a4323ec67f7c9528cbdbf6a06a8524494501`, run `34800084225`, green Python 3.10/3.11/3.12 jobs and 67 Python 3.11 tests. It explicitly lists stricter corpus-closure nodes that remain open.

Result: `PASS`.

## 6. Cross-document coherence findings

Two material inconsistencies were identified and corrected before issuing this certificate.

### Finding DOC-004-F01 — obsolete large persistent-storage requirement

**Before correction:** `MATERIALIZATION.md` described full-media execution as requiring a persistent self-hosted node with at least 120 GiB free.

**Conflict:** `ECHO-FREE-TIER-001` freezes standard public zero-cost execution and does not authorize paid/self-hosted capacity as the default solution to a working-set problem.

**Resolution:** materialization guidance now uses bounded shard/per-asset execution, durable compact evidence and raw-byte deletion. Sources that cannot close inside the boundary remain open or are replaced with defensible free paths.

**Result:** `CLOSED`.

### Finding DOC-004-F02 — stale statement that no Foundry implementation points remained

**Before correction:** `CURRENT-STATE.md` said there was no remaining hidden Foundry implementation point in DF-G0..DF-G8 and framed the remaining work primarily as external media execution.

**Conflict:** the deep-research closure pass identified real internal closure work: cross-format near-duplicate hardening/fixtures, dedicated hard-negative materialization/evidence integration, global ledger/group/source-independence integration and second-freeze reproducibility.

**Resolution:** `CURRENT-STATE.md` and `FOUNDRY-GATES.md` now expose these nodes explicitly while preserving the distinction between the certified baseline toolchain and the stricter final corpus certificate predicate.

**Result:** `CLOSED`.

No unresolved material documentation contradiction found in the audited current-authority set after these corrections.

## 7. Toolchain certificate coherence

The historical `CERT-MK1-DF-TOOLCHAIN-001` covered an older 42-test baseline. Material policy/coverage/source-snapshot changes occurred after it, so retaining it as the current certificate would violate its own invalidation clause.

Current engineering evidence:

```text
CERT-MK1-DF-TOOLCHAIN-002
baseline = be75a4323ec67f7c9528cbdbf6a06a8524494501
GitHub Actions run = 34800084225
Python 3.10 = PASS
Python 3.11 = PASS / 67 tests
Python 3.12 = PASS
```

Later commits before this audit changed documentation/materialization evidence, not the certified toolchain code/config/schema/test/workflow surface.

Result: certification ledger/current state now point to `CERT-MK1-DF-TOOLCHAIN-002` as the current engineering certificate.

## 8. Empirical honesty audit

The current documentation correctly keeps these claims open:

```text
EMP-DATASET-001         OPEN
EMP-DATA-QUALITY-001    OPEN
CERT-MK1-DF-CORPUS-001 OPEN
EMP-MODEL-001           OPEN
EMP-THRESH-001          OPEN
EMP-DIST-001            OPEN
EMP-CAP-001             OPEN
EMP-SLO-001             OPEN
EXT-CAMERA-001          EXTERNAL_GATE_OPEN
```

No documentation certificate is used to convert candidate/download counts into admitted counts, to claim zero real-media leakage before the global audit, or to announce a model winner before benchmark execution.

Result: `PASS`.

## 9. Semantic-boundary audit

Current authoritative documents preserve the frozen MK1 acoustic-event semantics and the important non-equivalences:

```text
Alarm      != FIRE_ALARM
Squeak     != TIRE_SQUEAL
Car        != VEHICLE_HORN
Glassware  != GLASS_SHATTER
```

`BACKGROUND_NO_TARGET` remains a data state; `UNKNOWN` remains decision-layer abstention.

Result: `PASS`.

## 10. Zero-cost boundary audit

Documentation now consistently states that:

```text
paid services/runners/storage/GPU/APIs/dataset access = not default-authorized
automatic overage = denied
quality threshold reduction to force closure = denied
bounded shard/per-asset execution = required strategy
uncloseable node inside boundary = OPEN / EXTERNAL_GATE_OPEN
```

Corpus closure, benchmark/model work and later MK evidence all inherit this rule.

Result: `PASS`.

## 11. Documentation governance hardening

This pass also adds machine enforcement:

```text
scripts/check_documentation_governance.py
.github/workflows/documentation-governance.yml
```

The checker fails closed on high-authority drift, including:

- immutable promise missing from charter/current state;
- documentation/free-tier frozen governance missing;
- current documentation/toolchain certificate mismatch;
- accidental promotion of `CERT-MK1-DF-CORPUS-001` before evidence;
- disappearance of closure-critical near-duplicate/hard-negative/reproducibility nodes;
- reintroduction of obsolete 120 GiB/self-hosted materialization requirements;
- Markdown corpus count drift without re-audit;
- merge-conflict markers in Markdown.

The workflow also executes `scripts/check_free_tier_boundary.py`, so documentation governance cannot silently introduce an execution path outside the zero-cost boundary.

Automated checks supplement human review; they do not replace scientific/license/semantic judgment.

## 12. Current certification hierarchy

```text
CERT-ECHO-000
       +
CERT-DOC-004
       +
ECHO-FREE-TIER-001
       ↓
certified technical ancestors
       ↓
required empirical evidence
       ↓
future certificate eligibility
```

For the current critical path:

```text
CERT-DOC-004                  CERTIFIED
CERT-MK1-DF-SPEC-001          CERTIFIED
CERT-MK1-DF-TOOLCHAIN-002     CERTIFIED
CERT-MK1-DF-CORPUS-001        OPEN
```

This is the intended state: documentation/tooling may be certified while the real corpus remains honestly open.

## 13. Certification decision

`CERT-DOC-004 = CERTIFIED` for the **206-file Markdown corpus** represented by the repository state containing this audit and the accompanying governance/current-state corrections.

Certification scope:

```text
document depth
reconstructibility
cross-document coherence
current-state/ledger alignment
zero-cost policy alignment
explicit separation of certified vs empirical/open claims
```

This certificate does not authorize skipping any Corpus Foundry empirical gate.

## 14. Invalidation

`CERT-DOC-004` becomes stale/invalid for current HEAD if any of the following occurs:

- a substantive Markdown file is added or materially rewritten without review;
- the 206-file corpus count changes without a new audit;
- an authoritative document regresses into a stub;
- current state, certification ledger/DAG and normative phase docs materially disagree;
- prose and machine-readable policy disagree on a material rule;
- a paid/overage path is presented as the default ECHO solution while `ECHO-FREE-TIER-001` remains frozen;
- empirical results are promoted without traceable evidence;
- the project promise/taxonomy/contracts change without downstream dependency review.

Historical documentation certificates remain immutable evidence for their own repository baselines; they are not rewritten to pretend they covered later work.
