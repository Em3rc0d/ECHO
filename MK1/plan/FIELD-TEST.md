# MK1 Field Test Plan

**Status:** `EXTERNAL_GATE_OPEN`

## Preconditions

Authorized camera/site access, known model/audio capability, RTSP/codec/network path, permitted test/capture policy, safe event playback/generation plan and external mic fallback if needed.

## Device characterization

Record camera/NVR model, firmware where available, microphone, codec, bitrate/sample rate/channels, AGC/noise settings, mounting/orientation and network transport.

## Connectivity tests

Probe RTSP stability, audio track, TCP/UDP behavior as applicable, reconnect after interruption/reboot and simultaneous client limits without exposing credentials in evidence.

## Acoustic matrix

Where safe/feasible: distance points such as 5/10/15/20/25 m, low/medium/high ambient noise, direct/oblique orientation, target examples that can be ethically/safely reproduced, plus matched hard negatives. These are test points, not guaranteed range.

## Metrics

Per-class detection/misses, confidence distribution, false alarms during continuous ambient capture, detection/alert latency, packet/decode issues and signal quality.

## Field holdout

Keep a subset untouched by tuning. If authorization only permits transient evaluation, derive allowed metadata/results and delete media according to policy.

## Safety/scope

Do not create dangerous incidents to generate sound. Use safe recordings/replay or benign controlled equivalents when real target generation is inappropriate.

## Output

Sanitized field evidence bundle closing applicable external gates and feeding distance/domain/SLO decisions.