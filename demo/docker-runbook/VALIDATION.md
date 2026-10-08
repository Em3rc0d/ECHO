# Demo Validation Checklist

Use this after the Docker services are running.

## A. Infrastructure

Run:

```bash
docker compose -f compose.mvp.yaml --profile demo ps
```

Expected:

- broker healthy/running;
- consumer running;
- demo running;
- UI reachable on `http://localhost:8088`.

## B. Controlled scenarios

Run each scenario from the UI:

1. Rotura de vidrio
2. Sirena
3. Bocina vehicular
4. Ambiente sin evento objetivo

These are governed controlled-validation presentation fixtures.

Their behavior must not be described as field performance.

## C. Blind WAV

Select a WAV through **Prueba ciega**.

Expected behavior:

- no expected label is supplied;
- audio is processed through the real selected scorer and temporal engine;
- external-audio diagnostics are displayed;
- output is constrained by the abstention decision layer.

## D. Microphone

Grant browser microphone permission.

Record at least the minimum shown by the UI, currently one complete 6 s analysis window.

Recommended manual probes:

### D1. Ordinary voice

Speak normally without reproducing any target event.

Purpose: exercise a known hard-negative/confuser family.

### D2. Ambient-only

Capture ordinary room/street/background sound with no target event.

Purpose: stress the environmental false-positive boundary.

### D3. Target-like external sound

Safely reproduce an allowed target sound from a speaker or benign source.

Purpose: show that the model may produce a target candidate while the external-audio decision layer still abstains because this path is not field calibrated.

Do not create dangerous events to test the demo.

## E. Decision-layer expectations

External audio has only two accepted demo outcomes:

### NO_TARGET

No current target was temporally confirmed.

Expected:

- no accepted target event;
- no target MQTT publication;
- score diagnostics can still be visible.

### UNKNOWN

One or more target candidates were internally confirmed, but external-domain acceptance is uncalibrated.

Expected:

- candidate shown as internal;
- candidate marked `NO PUBLICADO`;
- zero accepted target events;
- MQTT target publication suppressed;
- rationale identifies external-domain abstention.

## F. Known false-positive record

The following ad hoc observations motivated the current design:

- ~51 s ambient-only input previously emitted GLASS_SHATTER (~55%) and SIREN (~70%);
- ~4.1 s voice-only input previously emitted GLASS_SHATTER (~56%).

The short voice case also exposed repeated zero-padded tail windows and is now structurally contained.

The long ambient case remains an open MVP robustness issue.

See `../../MK1/test/FALSE-POSITIVE-ANALYSIS-2026-10-08.md`.

## G. Pass condition for the frozen demo

The demo is functionally acceptable when:

- container startup succeeds;
- all controlled scenarios execute;
- external WAV/mic input works;
- short external captures are not accepted as repeated padded evidence;
- external candidates are separated from accepted events;
- NO_TARGET / UNKNOWN are rendered correctly;
- external target candidates are not published to MQTT.

This is a **demo functional pass**, not a scientific or production certification.
