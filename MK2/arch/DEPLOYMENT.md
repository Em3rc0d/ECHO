# MK2 Deployment Architecture

**Status:** `PROFILE-BASED DESIGN`

## Deployment profiles

### Edge single-host

Sources on LAN -> ECHO runtime -> local broker/store. Lowest raw-audio network exposure and operational complexity; capacity bounded by host.

### Centralized inference

Multiple remote/edge ingest nodes -> secured network -> central worker(s)/broker. Better accelerator sharing/model rollout; higher network/privacy/failure dependence.

### Hybrid

Decode/preprocess/event buffering near sources with centralized inference or event services. Added complexity justified only by scale/site constraints.

## Deployment unit

Container/service packaging should pin code/dependencies/model/config/schema and expose health endpoints/metrics. Native FFmpeg/GStreamer/broker versions remain in SBOM/BOM.

## Network

Camera/source network, inference service and broker/store boundaries use least privilege. Avoid exposing RTSP/broker publicly. Time synchronization strategy documented.

## State

Runtime configuration/model artifacts are versioned; persistent event/model registry data has backup/migration policy. Ephemeral audio buffers are not backed up.

## Rollout

Staging -> limited/canary or controlled source subset -> full profile after SLO/regression checks, with rollback artifact retained.

## Capacity mapping

Each deployment profile names hardware, model, source count/rate and SLO envelope. No universal support number.

## Invalidation

Different organization/network/jurisdiction may require a distinct deployment/security profile.