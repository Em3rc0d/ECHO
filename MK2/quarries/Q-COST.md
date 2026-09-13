# Quarry — Cost Model

**Status:** framework `CERTIFIED`; deployment costs `EMPIRICAL`.

## 1. Purpose

Keep ECHO PoC free/open-source where practical while making hidden operational costs visible. “Software license cost = 0” does not mean total cost is zero.

## 2. Cost dimensions

```text
compute hardware
GPU/accelerator if used
camera/NVR/microphone equipment
network/switching
storage for event metadata/evidence
power
operator/maintenance time
cloud egress/compute if introduced
backup/monitoring
certificate/domain services if public-facing
```

## 3. Model-related cost

A heavier model can increase:

- hardware acquisition;
- power;
- number of nodes;
- deployment complexity;
- warm-up/update time.

Therefore model selection includes resource economics, not only F1.

## 4. Storage model

Default raw continuous audio retention is zero, substantially reducing storage and privacy exposure. If evidence clips are enabled, estimate:

```text
average clip size
alerts/day/source
retention days
replication/backup factor
```

## 5. Network model

If inference is local/edge, continuous camera audio stays LAN-local. Cloud centralization would create ongoing bandwidth/egress/privacy costs and must be justified separately.

## 6. Open-source licensing vs cost

Mosquitto/FFmpeg/model frameworks can be used without SaaS fees under their licenses, but compliance, integration and operations still cost time. Dataset/model licenses can also restrict intended use even when monetary price is zero.

## 7. Cost profiles

Maintain at least:

```text
PoC local profile
single-site edge profile
multi-site/centralized candidate profile
```

Do not extrapolate production TCO from a laptop demo.

## 8. Decision output

MK2 release should include a bill-of-materials and estimated cost per supported source/site for the certified hardware profile, with assumptions clearly listed.
