# MK1 Field-Audio Robustness Gate

**Status:** `OPEN / EMPIRICAL`  
**Profile:** `ECHO-MVP-001`  
**Scope:** ad hoc WAV and microphone/camera-like environmental audio only

## Purpose

Close the gap between controlled-validation temporal calibration and noisy real capture before ECHO expands its target taxonomy or makes field-performance claims.

This gate does **not** redefine the immutable ECHO promise and does not promote demo recordings into the governed train/validation/test corpus.

## Triggering observations

Two ad hoc demo observations on 2026-10-08 exposed target-free false positives:

- an approximately 51 s ambient-only recording produced logical events for `GLASS_SHATTER` (~0.55 peak) and `SIREN` (~0.70 peak);
- an approximately 4.1 s voice-only microphone capture produced `GLASS_SHATTER` (~0.56 peak) even though no glass event was present.

These are tester-reported field/demo observations. The raw recordings are not committed and therefore are **not reproducible benchmark evidence**.

The 4.1 s case also exposed a concrete replay/demo artifact: with a 6 s analysis window, 1 s hop and `pad_final=True`, a clip shorter than one full window could generate several overlapping zero-padded tail windows. That can manufacture repeated temporal evidence from essentially the same short signal.

## Immediate containment

External demo audio now follows a stricter ingestion boundary:

1. no zero-padded tail windows for user-uploaded or microphone audio;
2. at least one complete analysis window is required;
3. microphone captures shorter than the configured analysis window are rejected;
4. external-audio output is explicitly labeled experimental / not field calibrated;
5. per-window score diagnostics are returned without retaining raw audio;
6. MQTT reporting distinguishes zero event messages from actual event-message publication;
7. `ECHO-DEMO-ABSTENTION-v1` maps external audio to `NO_TARGET` or conservative `UNKNOWN` rather than accepting uncalibrated target candidates;
8. external target candidates are suppressed from target-event MQTT publication while remaining visible as diagnostics.

Controlled validation scenarios keep their existing calibrated replay behavior so prior temporal evidence is not silently redefined.

The detailed incident analysis and decision rationale are frozen in `FALSE-POSITIVE-ANALYSIS-2026-10-08.md`.

## Remaining false-positive quarry

The long ambient false positive remains unresolved. It must not be hidden by arbitrary score thresholds selected from one screenshot or one ad hoc clip.

For each target class, capture target-free environmental audio and report:

- total target-free source-hours;
- false events and false alarms/source-hour;
- peak/mean score distributions;
- windows at or above the current entry threshold;
- longest consecutive above-threshold run;
- confuser family: speech, traffic, music, machinery, impacts, alarms/tones, wind, other;
- device/input path and capture conditions.

The mining loop is:

```text
ambient / hard-negative capture
        ↓
score trace
        ↓
false-event localization
        ↓
confuser classification
        ↓
validation-side hard-negative experiment
        ↓
retrain / recalibrate if justified
        ↓
untouched field holdout
```

## Scientific constraints

- Do not tune thresholds directly against the final field holdout.
- Do not add a magic `0.8` or similar field threshold to make a demo look clean.
- Do not train on ad hoc professor-demo recordings unless they are deliberately admitted under a new governed corpus version.
- Do not claim that zero false alarms in a small demo implies production robustness.
- Model/preprocessing/taxonomy changes require threshold re-evaluation.

## Exit conditions

This gate can close only when:

1. the short-clip padding regression is verified in Docker;
2. target-free field/stress recordings have enough duration and diversity to characterize recurring confuser families;
3. the current model's false-alarm profile is measured by class;
4. any hard-negative or recalibration change is selected without test/field-holdout leakage;
5. a frozen candidate is evaluated on untouched environmental audio;
6. known limitations are recorded, including any class that remains too unstable for field use.

A numerical false-alarm ceiling must be frozen **before** the final holdout is inspected. This document intentionally does not invent that value from the two ad hoc observations.

## Relationship to ECHO-MVP-002

`ECHO-MVP-002` class expansion is design-only while this gate is open. New target classes increase the false-positive surface and therefore may not enter build/training merely to improve the demo.
