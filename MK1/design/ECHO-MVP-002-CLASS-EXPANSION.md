# ECHO-MVP-002 — Security Acoustic Class Expansion

**Status:** `DESIGN_ONLY / BUILD_BLOCKED`  
**Blocking gate:** `MK1/test/FIELD-AUDIO-ROBUSTNESS-GATE.md`  
**Implementation authorization:** **NO**

## Product boundary

The immutable promise remains:

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

MVP-002 expands observable acoustic-event classes. It does not infer crimes, emergencies, injuries or intent from sound alone.

## Proposed target set

The current MVP-001 classes remain:

- `GLASS_SHATTER`
- `SIREN`
- `VEHICLE_HORN`

MVP-002 proposes four additional targets:

- `SCREAM`
- `GUNSHOT`
- `FIRE_ALARM`
- `COLLISION_IMPACT`

Resulting proposed target count: **7**.

`BACKGROUND_NO_TARGET` and `UNKNOWN` remain decision/evaluation concepts, not automatically a mutually exclusive model class. `TIRE_SQUEAL` remains outside this proposed MVP-002 set unless separately re-authorized.

## Semantic contracts

### SCREAM

Acoustic evidence compatible with a scream or scream-like vocalization.

Must **not** be described as proof that a person is in danger.

Primary confusers: loud speech, laughter, children playing, singing/music vocals, crowd noise.

### GUNSHOT

Acoustic evidence compatible with a gunshot-like impulsive event.

Must **not** be described as confirmed firearm discharge without independent evidence.

Primary confusers: fireworks/firecrackers, balloon pops, doors/slams, hammer/construction impacts, engine backfire and other impulsive transients.

### FIRE_ALARM

Acoustic evidence compatible with a fire-alarm pattern.

Must **not** be described as confirmation of fire.

Primary confusers: timers, reversing beepers, security alarms, electronic chirps, appliance tones and music/synth tones.

### COLLISION_IMPACT

Acoustic evidence compatible with a high-energy collision/impact.

Must **not** be described as confirmation that a vehicle collision occurred.

Primary confusers: dropped metal/objects, construction impacts, doors, dumpsters, machinery and glass/ceramic impacts.

## Modeling implications

The current `PANNS_CNN14_HEAD` checkpoint has exactly three ECHO outputs. Adding UI labels does not add model capability.

A valid MVP-002 build requires a new benchmark identity and a new output head/target manifest. At minimum:

```text
new governed corpus version
→ 7-target supervision contract
→ group-aware split/freeze
→ benchmark A/B/C rerun
→ validation-side model selection
→ per-class error analysis
→ temporal calibration
→ untouched test
→ environmental/field robustness gate
```

No MVP-001 threshold or calibration artifact may be silently reused as an MVP-002 threshold version.

PANNs/AudioSet pretraining may contain useful representation knowledge for some proposed categories, but pretrained knowledge is not ECHO certification and does not waive ECHO-specific data/evaluation requirements.

## Data requirements

Each added class needs:

- release-safe positive examples from multiple independent recording/source families;
- explicit hard negatives matching likely confusers;
- group-aware train/validation/test separation;
- provenance, rights and hashes;
- device/domain diversity where available;
- an untouched environmental/field holdout when real capture is authorized.

Impulsive classes such as `GUNSHOT` and `COLLISION_IMPACT` require particular care with event timing because clip-level weak labels can make temporal onset metrics misleading.

## Event Engine

MVP-002 remains multi-label. Several acoustic events may coexist.

Each new class receives independent evidence-driven temporal parameters. A single global threshold is not authorized.

The Event Engine continues to own confirmation, hysteresis, release, cooldown and event lifecycle; the model remains a window scorer.

## Entry gate for implementation

Build/training is authorized only after the following are closed or explicitly waived with evidence:

1. MVP-001 short-external-audio repeated-padding behavior fixed and verified;
2. environmental target-free false positives characterized;
3. a hard-negative iteration completed without test leakage;
4. current three-class limitations documented;
5. corpus feasibility for all four proposed classes reviewed;
6. rights/licensing and split integrity remain compatible with the new benchmark.

Until then, MVP-002 is a **design contract only**.

## First experiments after authorization

When the gate closes, execute in this order:

1. corpus feasibility audit for the four new classes;
2. confuser taxonomy and hard-negative acquisition;
3. frozen seven-target manifest;
4. A/B/C benchmark without assuming PANNs remains winner;
5. validation-only calibration;
6. test and long target-free replay;
7. camera/environmental stress evaluation.

## Kill/pivot rule

A proposed class may be removed from MVP-002 if evidence shows insufficient release-safe data, unacceptable confusability, unstable field behavior or disproportionate false-alarm cost.

The product should ship fewer reliable acoustic classes rather than a larger unreliable label list.
