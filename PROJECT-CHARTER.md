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

ECHO owns acquisition through a source abstraction; normalization/preprocessing; AI-based inference; multi-label probabilities where concurrent events are possible; temporal event consolidation; source/timing propagation; confidence/calibration and abstention; structured event publication; quality measurement; multi-source orchestration; and privacy/security controls necessary to operate the acoustic pipeline.

### Out of scope as core promise

NVR/video product features, facial/person/object recognition, speech transcription, speaker identification, crime/intent interpretation, a generic smart-city platform, general dashboards, blockchain consensus and causal claims that cannot be established from sound alone are outside the defining promise.

## 4. Semantic boundary

```text
GLASS_SHATTER        != ROBBERY_CONFIRMED
IMPACT_SOUND         != VEHICLE_ACCIDENT_CONFIRMED
SIREN                != EMERGENCY_CONFIRMED
YELL/SCREAM          != PERSON_IN_DANGER_CONFIRMED
FIRE_ALARM_SOUND     != FIRE_CONFIRMED
```

Downstream systems may fuse ECHO events with video, human review or other sensors; that fusion is not automatically an ECHO truth claim.

## 5. Consumers

Security/operations dashboards, event stores, alerting services, analytics, mobile/web clients and research tooling may consume ECHO. They must depend on versioned contracts rather than internals of a particular neural network.

## 6. Source model

A source is a logical origin of acoustic samples identified by `source_id`: IP-camera audio, NVR stream, network/local microphone, recorded replay or synthetic test adapter. The PoC may use one physical camera while contracts remain multi-source.

## 7. Event lifecycle

```text
RAW_INFERENCE      model score(s) for an analysis window
CANDIDATE_EVENT    temporal evidence accumulating
CONFIRMED_EVENT    one consolidated acoustic occurrence
ALERT/PUBSUB       routing/delivery representation
```

This prevents overlapping windows from becoming duplicate physical-event notifications.

## 8. Engineering principles

`EVIDENCE FIRST`: facts, inferences, hypotheses, decisions and targets are distinguishable.  
`BENCHMARK BEFORE PROMISE`: quality, distance, thresholds, source count and latency are measured.  
`MULTI-SOURCE BY DESIGN`: logical N-source support exists before physical scale claims.  
`CONTRACTS OVER COUPLING`: source/audio/inference/event interfaces are versioned.  
`PRIVACY BY DEFAULT`: continuous audio retention is not required.  
`FAIL EXPLICITLY`: overload, disconnect and unknown audio are observable states.  
`REPRODUCIBILITY`: data/model/config/runtime versions accompany evidence.  
`DOWNSTREAM INVALIDATION`: material upstream changes trigger dependency review.

## 9. Milestones

MK0 gathers state-of-art evidence and certifies protocols/design choices without inventing ECHO performance. MK1 constructs the first vertical and produces model/threshold/runtime evidence. MK2 hardens that vertical into a multi-source operable product with capacity, resilience, observability, security, release governance and model lifecycle.

## 10. Mandatory pipeline

```text
brainstorming -> design -> arch -> plan -> build -> test
```

`mining-site/` stores evidence/provenance and `quarries/` hold research workstreams; neither replaces a stage.

## 11. Build gate

No build is authorized while an unresolved decision can force a core redesign. Intrinsically empirical uncertainty is converted into a controlled experiment instead of being guessed.

```text
model winner          -> empirical output; build may proceed
threshold values      -> empirical output; build may proceed
camera credentials    -> external gate; replay build may proceed
source identity model -> architecture decision; must close before build
```

## 12. Success definition

ECHO succeeds when it fulfills the fixed promise inside a documented operating envelope with reproducible evidence and known limitations. “100% functional” means all requirements in certified scope pass, not perfect ML accuracy.

## 13. Change control

Editorial clarification does not invalidate scope. A refined implementation principle triggers dependency review where relevant. A changed product boundary or promise invalidates downstream certificates and constitutes a major product revision.