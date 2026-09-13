# MK1 Configuration Specification

**Status:** `FROZEN_SCHEMA_INTENT`

## Configuration domains

`runtime`: mode replay/live, worker/scheduler settings.  
`sources`: source IDs/types, non-secret adapter options, secret references.  
`audio`: canonical rate/channels/window policy.  
`model`: artifact ID/path/hash/preprocessing.  
`event_engine`: per-class thresholds/temporal parameters/version.  
`mqtt`: broker host, topic root, QoS/retain policy, auth secret refs.  
`observability`: log/metric levels without sensitive data.

## Validation

Unknown/invalid fields fail startup rather than falling back silently. Numeric ranges such as queue size, thresholds and durations are validated. Config schema/version is recorded in build manifest.

## Secrets

Use `${SECRET_REF}`/environment/secret-store indirection. Redacted config dumps may show key names but not values.

## Modes

Offline benchmark may choose no-drop/blocking scheduler while live mode uses bounded freshness policy. Mode differences are explicit and cannot silently alter benchmark results.

## Overrides

CLI/environment override precedence must be deterministic and documented. Final effective config (redacted) is hashable for evidence.

## Invalidation

Breaking config changes require schema/version bump and update of fixtures/deployment docs.