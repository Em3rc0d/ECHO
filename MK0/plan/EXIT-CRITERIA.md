# MK0 Exit Criteria

**Status:** `PASS / CERT-MK0-013`

## Principle

MK0 ends when the project can start the first build without unresolved architecture-changing assumptions. It does not wait for empirical values that only implementation/tests can produce.

## Required closure

- fixed promise and semantic anti-scope;
- system boundary and multi-source invariant;
- v1 target taxonomy and unknown/background semantics;
- model landscape and minimum A/B/C benchmark;
- data admission, license, split and field-holdout policy;
- source/RTSP abstraction and decoder baseline;
- inference -> candidate -> confirmed event lifecycle;
- Pub/Sub candidate/semantics;
- privacy/security baseline;
- risk register;
- benchmark/test protocol;
- explicit external gates;
- MK1 DoR.

## Allowed open outputs

Model winner, numerical thresholds, measured latency/resources, supported N, distance/SNR envelope and final SLOs remain open because they are outputs of MK1/MK2 evidence.

## External gate handling

Real-camera model/audio/codec/network/permission may remain `EXTERNAL_GATE_OPEN` if a replay path can exercise the same core contracts. This prevents a hardware delay from corrupting the design process.

## Fail conditions

MK0 is not valid if a target has no defensible semantic/data path, if benchmark protocols use leaked/test-tuned data, if source/event semantics are still ambiguous, or if the repo marks aspirational metrics as measured facts.

## Evidence

See `MK0/test/MK0-GATE.md`, `MK0/test/MK0-CERTIFICATE.md`, `governance/CERTIFICATION-LEDGER.md` and the MK0 web audit.

## Invalidation

Material changes to promise, taxonomy, source contract, event schema, benchmark set or privacy policy trigger selective recertification.