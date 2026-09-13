# MK1 Dependency Policy

**Status:** `FROZEN_BASELINE`

## Principle

Dependencies are selected for a defined role, pinned sufficiently for reproducibility and audited for license/provenance. “Latest” is not a build identity.

## Categories

Runtime/framework dependencies; audio/ML libraries; model/checkpoint artifacts; FFmpeg/GStreamer system binaries; MQTT client/broker; test/benchmark tooling.

## Rules

- lock direct/transitive package versions using chosen ecosystem tooling;
- record Python/runtime and native binary versions;
- pin model/checkpoint hash independently from model code;
- avoid unnecessary overlapping frameworks unless benchmark requires them;
- prefer official packages/repos for model assets;
- record license/notice obligations in `THIRD_PARTY.md`/release inventory;
- do not bundle restricted data as a dependency.

## Upgrade policy

Upgrade intentionally in a separate change, rerun relevant unit/model/runtime regressions and compare artifacts. Security fixes may accelerate update but still require compatibility evidence.

## Native tools

FFmpeg build flags/plugins can affect codecs and license; record exact binary/version/build info rather than only package name.

## Supply chain

Hashes/checksums for checkpoints and downloaded artifacts; do not execute unreviewed remote model code with broad privileges.

## Invalidation

A dependency update affecting preprocessing, numerical output, codec behavior or delivery semantics invalidates corresponding result bundles.