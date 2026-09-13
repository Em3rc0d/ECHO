# MK1 Data Foundry — Field Holdout Design

**Status:** `SPECIFIED / EXTERNAL_GATE_OPEN`

## 1. Purpose

Public datasets cannot certify performance on the actual camera/microphone/network domain. The field holdout is ECHO's protected evidence set for measuring domain shift after `EXT-CAMERA-001` or an authorized microphone fallback becomes available.

## 2. Separation principle

Field holdout is isolated from:

- model training and fine-tuning;
- architecture choice;
- hard-negative training decisions derived from the same clips;
- threshold/calibration selection;
- Event Engine temporal parameter tuning;
- augmentation parameter tuning.

If field evidence causes a design change, the old field holdout becomes development evidence and a new untouched holdout must be collected before final certification.

## 3. Capture metadata

Each authorized recording/event should preserve at least:

```text
field_campaign_id
site_id (pseudonymous)
source_id
device/camera/microphone model
firmware when relevant
codec / sample rate / channels / bitrate
capture transport if relevant
distance band
orientation/mounting context
ambient-noise condition
weather/environment notes when material
event class / no-target label
onset/offset or event time when known
annotation procedure / reviewer
permission/retention reference
asset hash
```

Do not put credentials, exact private addresses or unnecessary identity/speech information in the manifest.

## 4. Experimental dimensions

Field campaigns should vary one factor at a time where practical:

- distance bands;
- quiet/moderate/noisy background;
- source orientation/occlusion;
- day/night or relevant environment state;
- actual camera codec vs higher-quality microphone reference when possible;
- network impairment/reconnect experiments separately from acoustic-quality experiments.

These dimensions are evidence slices, not promises. The certified operating envelope is derived only after measured results exist.

## 5. Positive capture

Targets must be captured only through safe, authorized and controlled means. If a target cannot be recreated safely/ethically in the available environment, use permitted prerecorded/synthetic playback for pipeline tests and label it clearly as playback/simulation rather than natural field occurrence.

Playback evidence is not equivalent to a naturally occurring event because speaker frequency response, room acoustics and signal path can change the waveform.

## 6. Negative capture

Long target-free recordings are required to estimate false alarms/source-hour. Negative campaigns should include routine ambient conditions and target-specific confusers expected at the site.

## 7. Privacy and retention

Default principle: minimize raw audio retention. Keep only what is necessary for authorized evaluation, with defined access and retention. Metadata/results can often be retained longer than raw audio. Continuous speech-content analysis, ASR and speaker identification remain out of scope.

## 8. Holdout identity

A field holdout has its own manifest hash and campaign metadata. Device/firmware/codec/site changes can define a new domain profile and require new evidence rather than silently mixing incompatible captures.

## 9. Gate closure

`EXT-CAMERA-001` closes only when brand/model, audio capability, RTSP/profile access, codec/sample-rate, network/access permission and capture authorization are known. That closes connectivity uncertainty; it does **not** automatically certify distance/SNR/model quality.

## 10. Downstream evidence

Field holdout feeds:

- `EMP-DIST-001` distance/SNR envelope;
- field false-alarm/miss analysis;
- latency/codec impact;
- `EMP-SLO-001` final SLO decisions;
- final MK1 limitations/certificate.

Field data remains clearly separated from public benchmark results in every report.