# MK2 Configuration

**Status:** `TARGET_SPEC`

## Configuration hierarchy

Base application defaults -> deployment-profile config -> site/source inventory -> model/event-engine bundle -> secret references -> controlled runtime overrides.

## Properties

Typed/schema validated; versioned; redacted effective dump; immutable per release where practical; clear precedence; no plaintext secrets; backward-compat migration when config schema changes.

## Source config

Logical identity, adapter endpoint/profile, enable state, site metadata, secret ref, optional service class. Device-specific codec settings remain adapter-level.

## Runtime config

Queue capacities, worker counts, batching/deadlines and backpressure policy are profile-specific and justified by capacity tests.

## Model config

Active model bundle references checkpoint/preprocessing/calibration/threshold/EventEngine config as compatible set.

## Delivery config

Broker endpoints, TLS/auth refs, topic namespace, QoS/durability/outbox parameters.

## Validation

Startup fails on incompatible model/schema/config or unsafe unbounded settings. Config hash appears in release/event evidence.