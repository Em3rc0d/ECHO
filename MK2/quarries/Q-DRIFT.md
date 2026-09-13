# Quarry — Data/Model Drift

**Status:** monitoring design `CERTIFIED`; production thresholds `EMPIRICAL`.

## 1. Purpose

Detect when deployment audio no longer resembles the conditions under which ECHO was validated. Drift can occur without code/model changes.

## 2. Drift sources

```text
new camera/microphone
firmware/audio codec changes
season/weather
construction/new machinery
traffic pattern changes
microphone degradation/obstruction
site layout changes
new recurring alarms/sounds
class prevalence changes
```

## 3. Signals

Monitor privacy-preserving aggregates where possible:

```text
score distributions by class/source
abstention rate
confirmed event rate
false-positive feedback rate
RMS/dBFS/silence statistics
embedding distribution summaries if justified
codec/device metadata changes
```

## 4. Ground-truth problem

Drift detectors alone cannot tell whether model quality actually fell. Maintain periodic labeled audits or reviewed event samples for real quality estimates.

## 5. Trigger hierarchy

```text
OBSERVE -> INVESTIGATE -> VALIDATE -> RECALIBRATE/RETRAIN -> SHADOW -> PROMOTE
```

Never auto-retrain/promote solely because an unsupervised drift score crosses a threshold.

## 6. Threshold recalibration

If representation remains good but score calibration shifts, threshold/calibrator update may be sufficient. If error families change, retraining/data expansion may be necessary.

## 7. Source-specific drift

One camera can drift while fleet-wide aggregates look healthy. Monitoring keeps source-level views and can quarantine/degrade one source without invalidating all others.

## 8. Model governance

Any retrain/recalibration produces a new version with dataset/config hashes and regression tests against historical holdouts. Previous certified model remains rollback candidate until new release passes gates.
