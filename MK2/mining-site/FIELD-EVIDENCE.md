# MK2 Field Evidence

**Status:** `PENDING_REAL_DEPLOYMENT`

## Purpose

Aggregate real-device/site evidence used to validate production operating envelopes while preserving privacy and deployment context.

## Record fields

Site/source/device identifiers using approved non-sensitive IDs; firmware/codec/mic/mounting; network profile; model/config/release; time period; ambient conditions; source health; event/false-alarm/miss evidence; latency; permission/retention reference.

## Domain slices

Where data supports it, summarize by device class, distance/SNR/noise, weather/orientation and time context. Small samples are reported as observations, not universal guarantees.

## Holdout governance

Some field data remains holdout-only for release evaluation. Production errors chosen for future training enter a new governed corpus version, never silently alter the historical holdout.

## Privacy

Store metadata/results in Git, not unrestricted raw audio. Evidence clips follow approved external storage/access/retention and are referenced by governed identifiers/hashes.

## Invalidation

Camera firmware/hardware/site or major preprocessing change can create a new domain profile requiring fresh evidence.