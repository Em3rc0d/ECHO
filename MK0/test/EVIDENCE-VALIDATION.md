# Evidence Validation — MK0

**Status:** `CERTIFIED_METHOD`

## Evidence hierarchy

1. standards/specifications and official project documentation;
2. original papers and author repositories;
3. official dataset release/DOI pages;
4. original open-source project docs/code;
5. secondary explanations only when primary evidence is unavailable or for context.

## Validation fields

For each evidence node record source URI, publisher/maintainer, accessed/release context when relevant, exact claim supported, ECHO implication, confidence and license/provenance notes.

## Cross-checking

Cross-check high-impact facts when one source may be stale or ambiguous—especially model/checkpoint licenses, dataset terms, protocol support and deployment behavior. Absence from docs is not proof a feature is impossible.

## Related-project evidence

Frigate and similar systems can establish that a pattern such as per-camera audio detection + MQTT is operationally plausible. They cannot establish ECHO's model quality, capacity or field distance.

## License evidence

Repository license, checkpoint license, dataset release terms and individual asset license are distinct evidence nodes.

## Contradictions

Preserve contradictory findings in mining-site and mark the decision unresolved until scoped or tested. Do not silently choose the convenient source.

## Validation output

A source catalog and web-audit ledger feeding certificates in `governance/CERTIFICATION-LEDGER.md`.

## Invalidation

Material upstream changes, dead/mutated assets or corrected evidence require re-audit of dependent claims.