# Quarry — Acoustic Robustness

**Status:** test design `CERTIFIED`; measured envelope `EMPIRICAL`.

## 1. Purpose

Determine whether ECHO remains useful when audio differs from clean training clips. Robustness is a multidimensional envelope, not one accuracy number.

## 2. Robustness axes

```text
SNR/background level
distance
reverberation
microphone response
orientation/occlusion
codec + bitrate
sample rate
AGC/noise suppression
clipping/gain
packet gaps
polyphony
weather/wind
site-specific ambient patterns
```

## 3. Why public datasets are insufficient

Public environmental datasets often contain curated clips, varied microphones and web-derived media. Security cameras can have low-bitrate speech-optimized microphones, aggressive AGC, compression and fixed mounting. Therefore public-test performance establishes algorithmic sanity, not field certification.

Frigate's audio documentation explicitly notes practical degradation from poor camera microphones, distance, low bitrate and background noise; this is useful operational evidence: https://docs.frigate.video/configuration/audio_detectors/ .

## 4. Test matrix

For each target class and finalist model, evaluate controlled strata where data allows:

```text
clean/reference
+ low/medium/high background noise
+ codec/transcode variants
+ gain/clipping variants
+ reverberation variants
+ field distance strata
```

Synthetic corruption never substitutes for real field holdout; it is sensitivity analysis.

## 5. SNR

Report performance by SNR bucket when ground truth permits. The exact SNR estimation method must be documented because environmental events do not always offer a clean signal/noise decomposition.

## 6. Distance

Distance is not a model-only property. It depends on event loudness, microphone, orientation, environment and codec. ECHO therefore treats distance as a field-test variable and does not promise a universal meter value in MK0.

Initial field test points such as 5/10/15/20/25 m are experimental points, not product guarantees.

## 7. Codec/transient sensitivity

Short transients such as shattering can be particularly sensitive to microphone bandwidth, AGC and compression. The actual camera codec should be used to create replay/transcode comparisons where legally/technically feasible.

## 8. Hard-negative robustness

Build a class-by-confuser matrix rather than only generic background:

```text
rows = target events
columns = confuser families
cell = FP rate / score distribution / reviewed examples
```

This directly identifies whether, for example, metal impact is a dominant GLASS_SHATTER failure.

## 9. Long negative replay

Balanced clips exaggerate target prevalence. Continuous negative recordings are required to estimate operational false alarms/source-hour.

## 10. Polyphony

Test target + background and target + target overlap. ECHO's multi-label contract should permit simultaneous events, but representation and Event Engine may still fail under masking.

## 11. Augmentation policy

Useful candidates include gain, additive environmental noise, time/frequency masking and controlled reverberation; however every augmentation must have a plausible domain rationale and ablation evidence. Avoid augmentation that produces acoustically impossible examples simply to increase diversity.

## 12. Acceptance philosophy

No robustness claim is certified unless it identifies the condition tested. Prefer:

```text
Recall(GLASS_SHATTER) at condition X
false alarms/hour on corpus Y
```

over “93% accurate in noise”.

## 13. Invalidation conditions

Revisit robustness design when target hardware changes, codec settings change materially, taxonomy expands or field errors reveal a missing domain factor.
