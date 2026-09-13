# Acoustic Taxonomy Candidates — MK0

**Status:** `SUPERSEDED_BY_MK1_V1 / HISTORICAL_EVIDENCE`

## Purpose

Document how candidate acoustic labels were screened before freezing MK1. This file preserves rejected/deferred reasoning so future teams do not rediscover the same ambiguity.

## Candidate screening criteria

A target must be an observable sound, have enough semantically valid/licensable evidence to support an experiment, have identifiable confusers, fit continuous-stream evaluation and avoid implying context not present in audio.

## Candidate set considered

| Candidate | Acoustic observability | Data/semantic notes | MK1 outcome |
|---|---|---|---|
| glass break/shatter | high | AudioSet has shatter; glass mapping needs semantic review | `GLASS_SHATTER` selected |
| siren | high | distinct but overlaps alarms/music sweeps | selected |
| fire alarm | high/medium | must not map generic alarm blindly | selected |
| vehicle horn | high | clear ontology support; tonal confusers | selected |
| tire squeal | medium/high | friction/squeal confusers | selected |
| generic alarm | high | semantically broad; overlaps fire/security/beeps | split/refined |
| vehicle collision | medium | impact sound does not prove vehicle collision | deferred |
| strong impact | medium | acoustically valid but broad/heterogeneous | deferred/control negative family |
| scream/yell | medium | high variability, speech/cheering confusers, privacy sensitivity | deferred |
| reversing beeper | high | useful but lower priority for first taxonomy | deferred/hard negative |
| dog bark | high | feasible but not aligned with initial security use-value | not selected |
| speech/music/traffic | high | useful as negative/context rather than targets | negative families |

## Frozen v1 result

```text
GLASS_SHATTER
SIREN
FIRE_ALARM
VEHICLE_HORN
TIRE_SQUEAL
```

`BACKGROUND_NO_TARGET` describes non-target training/evaluation context. `UNKNOWN` is an abstention state when target evidence is insufficient; it need not be a learned output neuron.

## Multi-label rule

Targets are not assumed mutually exclusive. A horn and siren can coexist, so model/evaluation contracts use independent target probabilities rather than forced softmax exclusivity.

## Mapping rule

String similarity never proves class equivalence. Upstream label mapping records EXACT/NARROWER/BROADER/AMBIGUOUS/NEGATIVE/UNUSABLE. Example: generic `Alarm` cannot become `FIRE_ALARM` without evidence.

## Risks

Too narrow a taxonomy may reduce available data; too broad a class can hide distinct confusers. Label ambiguity sets a ceiling on measurable performance and must be addressed through annotation review rather than model complexity alone.

## Validation

The selected targets must survive asset/license filtering and class-level error analysis. If one class lacks independent/diverse examples after deduplication, reopen its mapping or taxonomy before presenting benchmark conclusions.

## Invalidation

A new target requires downstream review of manifests, model head, metrics, thresholds, event schemas and consumers.