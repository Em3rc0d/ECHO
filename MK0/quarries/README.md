# MK0 / Quarries

Quarries are **deep research workstreams**, not question lists. Their job is to turn uncertainty into traceable evidence and then into either a closed engineering decision, a controlled MK1 experiment or an explicit external gate.

Every quarry follows:

```text
question
  -> evidence
  -> alternatives
  -> synthesis
  -> candidate decision
  -> validation protocol
  -> closure / invalidation conditions
```

Active/retained quarries:

```text
Q-MODELS.md
Q-DATASETS.md
Q-STREAMING.md
Q-EVENT-ENGINE.md
Q-PUBSUB.md
Q-MULTISOURCE.md
Q-ROBUSTNESS.md
Q-OPENSET-OOD.md
Q-SECURITY.md
Q-PRIVACY-LICENSING.md
```

A quarry can be `CERTIFIED_FOR_ARCHITECTURE` while empirical outputs remain pending. Example: multi-source boundaries and bounded queues can be certified now; the exact maximum source count cannot be certified until load/soak tests.

Substantive quarry documents must follow `governance/DOCUMENTATION-STANDARD.md`. README files are navigation artifacts and may remain shorter.
