# MK1 Test Matrix

**Status:** `FROZEN_PLAN / RESULTS_PENDING`

| Area | Test | Key evidence |
|---|---|---|
| config | valid/invalid schema + secret redaction | startup results |
| replay | deterministic decoding/window sequence | golden hashes/timestamps |
| audio | resample/downmix/window fixtures | sample/timing comparisons |
| model | A/B/C common test predictions | metrics + hashes |
| leakage | group/split/duplicate audit | zero forbidden overlap report |
| calibration | validation thresholds/reliability | curves/config |
| EventEngine | state transitions/boundaries/gaps | deterministic event logs |
| streaming | long positive/negative replay | FA/source-hour + misses |
| multi-source | concurrent replays | identity/fairness/drop metrics |
| overload | bounded queue | max memory/lag/drop behavior |
| source fault | disconnect/reconnect/generation | recovery log |
| MQTT | duplicate/reconnect/broker restart | event_id/idempotency evidence |
| persistence | event query/replay identity | stored records |
| security | secret/log/ACL/checksum tests | audit report |
| privacy | no default raw media retention | filesystem/temp audit |
| camera | RTSP/audio/codec/reconnect | external field evidence |
| distance/domain | SNR/distance/site matrix | field report |

## Requirement mapping

Each FR/NFR from `MK1/design/REQUIREMENTS.md` maps to at least one test. Missing mapping blocks certification.

## Result status

`NOT_RUN`, `PASS`, `FAIL`, `PARTIAL`, `EXTERNAL_GATE_OPEN`. Partial requires explicit uncovered behavior.

## Regression

Selected golden/unit/E2E cases become MK2 regression suite after MK1 certification.