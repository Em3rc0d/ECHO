# MK2 Retention and Privacy Design

**Status:** `DESIGN_SPECIFIED / DEPLOYMENT POLICY REQUIRED`

## Default

Continuous raw audio retention remains off. Production stores structured events, health and operational metrics needed for the declared service.

## Data classes

`EPHEMERAL_AUDIO`: in-memory bounded samples/windows.  
`EVENT_METADATA`: event/source/model/config/timing data.  
`OPERATIONAL_LOGS`: redacted system/health records.  
`EVIDENCE_CLIP`: optional authorized clip with strict purpose/retention/ACL.  
`FIELD_DATASET`: governed research asset with permitted-use metadata.

## Retention matrix

Exact days are deployment policy, not universal. Each data class specifies purpose, owner, storage location, access roles, retention, deletion method and legal/institutional basis where applicable.

## Minimization

No ASR/speaker ID/voice profile. Avoid source labels containing unnecessary personal/location detail. Do not put raw audio or credentials into telemetry.

## Evidence clip controls

Disabled by default. If enabled: trigger conditions, pre/post buffer, encryption/access, audit trail and automatic deletion are explicit. Clip capture never becomes an undocumented debug side effect.

## Data subject/incident considerations

Deployment operators must support applicable institutional/legal handling of access, deletion, breach or policy requests; exact obligations depend on environment/jurisdiction.

## Validation

Retention configuration tests, delete verification, temp/crash artifact scan, access-control review and audit-log checks.

## Invalidation

New jurisdiction, cloud storage, speech/biometric feature or longer media retention reopens privacy design.