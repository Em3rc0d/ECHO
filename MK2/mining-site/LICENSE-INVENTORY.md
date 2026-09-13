# MK2 Release License Inventory

**Status:** `TEMPLATE / RELEASE_BOM_PENDING`

## Purpose

Record the exact licensing/provenance of what a distributable release actually ships or references, not generic project candidates.

## Per component fields

Name/version/digest, role, source URI/package, license/SPDX where known, bundled vs external, modification status, notice/attribution requirement, source-offer/copyleft requirement if applicable and approval status.

## Model fields

Architecture code license, checkpoint URI/hash/license, pretraining-data provenance and redistribution terms separately.

## Dataset fields

Training/evaluation datasets are usually not bundled; still record release and permitted use. Any bundled sample/media requires asset-level license/provenance.

## Native binaries

FFmpeg/GStreamer/plugins/broker/container base packages are inventoried from actual build. Do not rely on a generic license statement when build flags/plugins change obligations.

## Release gate

Unknown/incompatible license or missing required notices blocks distributable certification or causes component removal/replacement.

## Current state

Policy is ready; exact inventory is generated from MK2 release candidate/SBOM.