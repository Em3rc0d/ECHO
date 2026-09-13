# ECHO Project Charter

**Status:** `CERTIFIED_SCOPE_AUTHORITY`  
**Certificate dependency:** `CERT-ECHO-000`

## 1. Immutable promise

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

This sentence is the law of scope for ECHO. A milestone may refine implementation, supported event classes, operating envelope, deployment topology or interfaces, but it cannot silently redefine this promise. A materially different promise constitutes a different product and requires explicit governance action.

## 2. Problem statement

Environmental audio is continuous, unstructured and difficult to supervise across multiple physical points. Traditional camera/NVR systems may record audio, but recording alone does not transform it into structured acoustic observations. ECHO addresses the engineering problem of continuously transforming audio into detectable/classifiable acoustic events that can be measured, time-bounded, associated with a source and consumed by other systems.

The project is therefore not justified by “using AI on sound”; AI is the mechanism used to implement the detection/classification promise.

## 3. Product boundary

### In scope

ECHO owns:

- acquisition of an audio signal through a source abstraction;
- normalization/preprocessing required for acoustic inference;
- AI-based inference over one or more target event classes;
- multi-label probabilities where concurrent events are possible;
- conversion of model windows into temporal events;
- source identity and timing propagation;
- confidence/calibration and abstention/unknown behavior;
- event publication through structured contracts;
- measurement of model/runtime quality;
- multi-source orchestration required for the acoustic pipeline;
- privacy/security controls necessary to operate that pipeline responsibly.

### Out of scope as core promise

The following may be integrations but are not ECHO's defining objective:

- NVR/video recording product features;
- facial/person/object recognition;
- speech transcription or speaker identification;
- interpretation of crimes, intent or social situations;
- a general-purpose smart-city platform;
- a generic dashboard product;
- blockchain/network consensus;
- guaranteed causal interpretation from sound alone.

## 4. Semantic safety boundary

ECHO classifies observable acoustic phenomena. It does not elevate a sound signature into a social/legal conclusion without other evidence.

```text
GLASS_SHATTER        != ROBBERY_CONFIRMED
IMPACT_SOUND         != VEHICLE_ACCIDENT_CONFIRMED
SIREN                != EMERGENCY_CONFIRMED
YELL/SCREAM          != PERSON_IN_DANGER_CONFIRMED
FIRE_ALARM_SOUND     != FIRE_CONFIRMED
```

Downstream systems may combine ECHO events with video, human review or other sensors; that fusion is outside the acoustic classifier's truth claim unless separately specified.

## 5. Users and consumers

Potential consumers include security/operations dashboards, event stores, alerting services, analytics, mobile/web clients and research evaluation tooling. ECHO must expose machine-readable contracts so these consumers do not depend on internals of a specific neural network.

## 6. Source model

A source is a logical origin of acoustic samples identified by `source_id`. It may be:

```text
IP camera audio track
NVR-exposed stream
network microphone
local microphone
recorded file/replay source
synthetic test adapter
```

The PoC may use one physical camera; contracts remain multi-source so adding a second source does not change domain objects.

## 7. Product event lifecycle

ECHO distinguishes four semantic levels:

```text
RAW_INFERENCE
    model score(s) for one analysis window

CANDIDATE_EVENT
    temporal evidence accumulating for a possible event

CONFIRMED_EVENT
    one consolidated acoustic occurrence satisfying event rules

ALERT/PUBSUB
    delivery/routing representation derived from a confirmed event
```

This separation prevents one physical event from producing dozens of notifications simply because overlapping windows produce multiple positive scores.

## 8. Scientific/engineering principles

`EVIDENCE FIRST`: external facts and measured results are separated from hypotheses and decisions.

`BENCHMARK BEFORE PROMISE`: accuracy, recall, distance, thresholds, source count and latency are measured rather than guessed.

`MULTI-SOURCE BY DESIGN`: logical contracts support N sources even when first hardware validation uses one.

`CONTRACTS OVER COUPLING`: source, audio, inference, event and Pub/Sub interfaces are versioned boundaries.

`PRIVACY BY DEFAULT`: continuous audio retention is not required to fulfill the promise.

`FAIL EXPLICITLY`: overload, disconnect, unknown audio and unavailable hardware are states to expose, not hide.

`REPRODUCIBILITY`: data/model/config/runtime versions and hashes accompany evidence.

`DOWNSTREAM INVALIDATION`: material upstream changes trigger dependency review.

## 9. Milestone model

### MK0

Collects Internet/state-of-art evidence, identifies viable datasets/models/protocols, defines risks and certifies the first build protocol. It may not claim empirical ECHO performance that has not been measured.

### MK1

Builds the first complete vertical and produces the empirical evidence needed for a defensible model, thresholds, event parameters and operating envelope. Real-camera integration is a branch of MK1 gated by hardware/access.

### MK2

Hardens the vertical into a robust multi-source product with capacity, resilience, observability, security, release governance, model lifecycle and reproducible operations.

## 10. Mandatory internal pipeline

Every MK follows:

```text
brainstorming -> design -> arch -> plan -> build -> test
```

`mining-site/` stores evidence/provenance. `quarries/` hold research workstreams. Neither replaces the six-stage pipeline.

## 11. Build gate rule

No build is authorized while an unresolved decision can still force a core redesign. Uncertainty that is intrinsically empirical may be converted into a controlled experiment and therefore does not need a fictional answer before build.

Examples:

```text
model winner          -> empirical MK1 output, build may proceed
threshold values      -> empirical MK1 output, build may proceed
camera credentials    -> external gate, replay build may proceed
source identity model -> architecture decision, must be closed first
```

## 12. Success definition

ECHO succeeds when it fulfills the fixed promise inside a documented operating envelope with reproducible evidence and known limitations. “100% functional” means all requirements in that certified scope pass; it does not mean 100% ML accuracy or zero uncertainty.

## 13. Charter invalidation/change control

Changes to this charter are classified:

- editorial clarification: no scope invalidation;
- refined implementation principle: review dependent decisions;
- changed semantic product boundary or promise: invalidate downstream certificates and treat as major product revision.

The active charter is referenced by the certification ledger and must remain traceable through Git history.