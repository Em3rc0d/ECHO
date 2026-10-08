# ECHO — False Positive Analysis and Demo Robustness Record

**Status:** `ACTIVE_EVIDENCE_RECORD`  
**Date:** 2026-10-08  
**Profile:** `ECHO-MVP-001`  
**Related:** issues #52, #53, #54

## 1. Scope of this record

This document captures the false positives observed while moving the professor demo from governed validation audio toward ad hoc microphone/WAV input.

It separates:

- empirical observations from the demo;
- confirmed implementation defects;
- model/domain hypotheses;
- containment already merged;
- unresolved scientific work that belongs to the real MVP rather than to presentation polish.

The raw ad hoc recordings are not committed, so the observations below are **tester-reported field/demo evidence**, not reproducible benchmark assets.

## 2. Current three-class model

The active MVP classifier has exactly three learned ECHO outputs:

```text
GLASS_SHATTER
SIREN
VEHICLE_HORN
```

The selected benchmark arm is `PANNS_CNN14_HEAD`: a pretrained PANNs Cnn14 embedding backbone followed by an ECHO multilabel head.

The head uses independent sigmoid outputs. Therefore the model is **not mathematically forced to choose one of the three labels**. It can score all three below their thresholds. Nevertheless, previously unseen or weakly represented sounds can activate one or more target heads because their learned acoustic representation overlaps with target regions.

## 3. Observed false positives

### FP-001 — ambient-only recording

Tester statement: the recording contained only ordinary environmental/ambient sound and none of the three target events.

Observed demo output:

- duration: approximately 51 s;
- `GLASS_SHATTER`: logical event, peak model score ~0.55;
- `SIREN`: logical event, peak model score ~0.70;
- two logical target events were emitted by the then-current external-audio path.

Interpretation:

- this recording was long enough that the later short-clip padding defect does not explain the whole failure;
- this remains a real environmental-domain false-positive signal;
- exact root cause is not yet established because the source audio is not preserved as governed evidence.

Status: **UNRESOLVED MODEL/DOMAIN ROBUSTNESS ISSUE**.

### FP-002 — voice-only microphone recording

Tester statement: the recording contained the tester's voice and no glass break.

Observed demo output:

- duration: approximately 4.1 s;
- `GLASS_SHATTER`: logical event;
- peak model score ~0.56;
- demo reported five analyzed windows.

This exposed two distinct problems:

1. **model/domain confusion:** speech produced a non-trivial GLASS_SHATTER score;
2. **confirmed demo/replay artifact:** the 4.1 s clip was shorter than the configured 6 s analysis window, yet `pad_final=True` produced several overlapping zero-padded windows at 1 s hops. Those windows repeatedly presented essentially the same short signal to the temporal engine and could manufacture repeated evidence.

Status:
- padding/repeated-evidence defect: **CONTAINED**;
- speech-vs-glass representation/confuser problem: **OPEN FOR MVP ROBUSTNESS WORK**.

## 4. Why this can happen

The working hypothesis is open-set/domain-shift behavior, not a forced-choice classifier.

Simplified flow:

```text
new environmental sound
        ↓
PANNs acoustic embedding
        ↓
ECHO three-output head
        ↓
some learned target head may activate
        ↓
Temporal Event Engine may confirm it
```

A voice, traffic sound, machinery, music, wind or other unseen/confusing sound can share spectral or temporal features with a trained target.

The important distinction is:

```text
"the highest target score is GLASS_SHATTER"
!=
"the input is known to be glass breaking"
```

The current MVP has conceptual `BACKGROUND_NO_TARGET` and `UNKNOWN` states at the decision layer, but the active checkpoint itself still has only the three target outputs.

## 5. Changes already merged

### 5.1 Short external-audio hardening

External microphone/WAV input now:

- disables zero-padded final replay windows;
- requires at least one complete analysis window;
- rejects microphone captures shorter than the configured window (currently 6 s);
- returns per-class score diagnostics;
- distinguishes external audio from governed validation scenarios.

This prevents a short recording from producing artificial repeated temporal evidence simply because it is padded at multiple hops.

### 5.2 Score diagnostics

For external audio the demo now exposes, per target:

- maximum model score;
- mean model score;
- current entry threshold;
- number of windows at/above entry threshold;
- longest consecutive run above threshold.

This is diagnostic evidence only. It is not a learned OOD distance.

### 5.3 Conservative abstention boundary

`ECHO-DEMO-ABSTENTION-v1` was added for uncalibrated external microphone/WAV input.

Decision semantics:

```text
external audio
    ↓
real ECHO scorer
    ↓
real Temporal Event Engine
    ↓
no target candidate ─────────→ NO_TARGET
target candidate(s) ─────────→ UNKNOWN / ABSTAIN
                                      ↓
                         target event NOT published
```

For `UNKNOWN`, the UI can still display internal target candidates and their model scores so the evaluator can see what the model suspected, but they are explicitly marked as unaccepted.

External target candidates are not published to MQTT.

### 5.4 No magic threshold

No arbitrary `0.8`, `0.9` or similar threshold was inserted to make the demo look cleaner.

Doing so from one or two ad hoc recordings would contaminate the engineering process and could suppress real distant/noisy events.

## 6. What the abstention layer does not solve

The current demo abstention boundary is deliberately conservative. It is **not** proof that ECHO now has a calibrated open-set detector.

Specifically, it does not yet provide:

- learned embedding-distance OOD rejection;
- energy/open-set calibration;
- a trained `TARGET / NO_TARGET` gate;
- camera-domain calibration;
- a measured acceptable false-alarm operating point;
- production-safe UNKNOWN acceptance thresholds.

Those remain MVP research/build work.

## 7. Correct next scientific work

The next robustness loop for the real MVP is:

```text
target-free environmental audio
        ↓
score traces + candidate localization
        ↓
confuser family classification
        ↓
hard-negative acquisition
        ↓
validation-side retraining / recalibration
        ↓
freeze candidate
        ↓
untouched field/environmental holdout
        ↓
false alarms per source-hour
```

Priority confuser families:

- speech / loud speech;
- music and tonal synth sounds;
- ordinary traffic and engines;
- metal/ceramic/dropped-object impacts;
- doors/slams;
- machinery;
- alarms/beepers/tones;
- wind/rain;
- construction;
- other recurring environmental sounds.

## 8. Operational metric

For environmental deployment, clip-level accuracy alone is insufficient.

A primary metric must be:

```text
false alarms per source-hour
```

Example only:

```text
3 false events / 100 target-free source-hours
= 0.03 false alarms per source-hour
```

The project must freeze an acceptable ceiling before inspecting the final field holdout.

No acceptable ceiling is invented in this document.

## 9. Relationship to future classes

The proposed MVP-002 expansion:

- `SCREAM`
- `GUNSHOT`
- `FIRE_ALARM`
- `COLLISION_IMPACT`

remains `DESIGN_ONLY / BUILD_BLOCKED`.

Adding more target heads increases the surface for accidental activations. The three-class robustness problem must first be characterized rather than hidden.

## 10. Demo scope conclusion

The professor demo is now intentionally frozen around:

- governed three-class validation scenarios;
- blind WAV upload;
- ephemeral microphone capture;
- score diagnostics;
- `NO_TARGET`;
- conservative `UNKNOWN / ABSTAIN`;
- MQTT for governed accepted events;
- suppression of uncalibrated external target candidates.

Further false-positive reduction belongs to the actual MVP engineering work, not to demo-specific tuning.

See:

- `demo/DEMO-SCOPE-FREEZE.md`
- `MK1/test/FIELD-AUDIO-ROBUSTNESS-GATE.md`
- `MK1/quarries/Q-HARD-NEGATIVES.md`
- issue #53
