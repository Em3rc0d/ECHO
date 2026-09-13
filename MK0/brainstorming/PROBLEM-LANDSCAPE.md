# Problem Landscape

**Status:** `CERTIFIED_PROBLEM_FRAMING`

## 1. Core problem

Environmental audio is continuous and unstructured. A camera/NVR can record it, but recording is not equivalent to automatically detecting a meaningful acoustic occurrence. ECHO must transform a stream into structured acoustic events with source, timing, class and confidence while controlling false alarms and latency.

## 2. Why clip classification is insufficient

Academic audio classifiers often receive isolated clips with a dominant event. A deployment receives hours of mostly negative audio, overlapping sources, compression, distance attenuation, reverberation, wind, speech, traffic and transient confusers. The operational denominator is therefore source-hours, not only balanced test clips.

## 3. Primary challenges

`DOMAIN SHIFT`: web/curated audio differs from IP-camera microphones and deployment sites.  
`FALSE POSITIVES`: even a tiny window-level error rate can create many alerts over continuous operation.  
`TEMPORAL AGGREGATION`: overlapping analysis windows must become one physical event.  
`MULTI-LABEL`: simultaneous acoustic phenomena are plausible.  
`MULTI-SOURCE`: source identity, buffers and event state must remain isolated.  
`REAL-TIME PRESSURE`: backlog can make alerts stale even when offline accuracy is high.  
`HARD NEGATIVES`: metal/ceramic impacts, beeps, music, brakes and machinery can resemble targets.  
`PRIVACY`: ambient audio may incidentally include speech although speech content is not needed by ECHO.

## 4. Observable-event boundary

ECHO can claim acoustic observations, not causes that require context. A glass-like shatter can be classified; a burglary cannot be concluded. This boundary improves scientific validity and reduces harmful overclaiming.

## 5. Stakeholders/consumers

Potential consumers include operators, academic evaluators, alerting applications and downstream fusion systems. They need stable contracts, not model-specific tensors.

## 6. Success dimensions

Success combines per-class detection quality, false alarms per source-hour, miss rate, latency, resource use, robustness to noise/domain shift and reproducibility. No single “accuracy” number captures the product.

## 7. Alternatives to an ECHO-specific pipeline

A fixed vendor camera detector can be simpler but limits class/model/data control. A general NVR such as Frigate validates parts of the pattern but ECHO remains a research/product pipeline centered on its acoustic promise, model benchmarking and evidence chain. Cloud-only inference may simplify compute provisioning but adds network/privacy/cost dependencies and is not required for the PoC.

## 8. Failure definition

ECHO fails even if a demo looks correct when it produces alert fatigue, misses critical targets under realistic SNR, cannot reproduce its metrics, leaks source state, accumulates unbounded latency, or bases claims on contaminated test data.

## 9. Downstream impact

This framing drives taxonomy design, hard-negative strategy, benchmark metrics, Event Engine design, multi-source architecture and field-test requirements.

## 10. Invalidation

Reframe if the target environment becomes fundamentally different (for example only curated uploads rather than continuous ambient audio) or the promise expands beyond acoustic detection/classification.