# Quarry — Robustness

**Status:** `PROTOCOL_CERTIFIED / RESULTS_EMPIRICAL`

## Purpose

Measure how detection degrades when deployment conditions differ from clean public clips. Robustness is an operating envelope, not a binary property.

## Axes

SNR/background type, distance, reverberation, orientation, microphone/device, codec/bitrate, sample-rate conversion, AGC/noise suppression, clipping, wind/weather, packet gaps and overlapping events.

## Target confusers

Glass vs metal/ceramic/dishes. Siren/fire alarm vs beeps/music/reversing beeper. Horn vs alarms/whistles/tonal machinery. Tire squeal vs brakes/metal/friction machinery.

## Controlled corruption matrix

Synthetic mixing/noise/reverb/transcode can identify sensitivity before field access. It must not be presented as proof of real-world robustness. Each transform records parameters and clean source identity.

## Field holdout

Actual camera/site recordings are the strongest domain evidence. Holdout remains untouched during training/threshold selection and is stratified by conditions when enough data exists.

## Metrics

Per-class recall/F1 vs SNR/condition, false alarms/source-hour on long negatives, calibration drift, latency/resource changes and failure examples.

## Augmentation

Training augmentation should approximate plausible deployment variation without generating artifacts that teach shortcuts. Evaluate augmentation by ablation on untouched data rather than assuming “more augmentation = better”.

## Failure analysis

Classify failures as representation, label ambiguity, preprocessing, threshold, Event Engine, signal quality or domain shift. This prevents blindly changing the neural network.

## Closure

MK0 closes only the robustness **protocol**. MK1/MK2 produce curves and field envelope.

## Invalidation

New hardware/site or preprocessing/model change requires relevant robustness regression.