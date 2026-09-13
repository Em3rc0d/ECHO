# MK0 -> MK1 Evidence Handoff

MK1 sólo consume evidencia certificada de MK0.

## Inputs esperados

- taxonomy decision + mapping;
- dataset manifests/licensing;
- model benchmark protocol;
- source/audio contracts;
- event lifecycle;
- pub/sub decision;
- privacy/security constraints;
- risk register;
- camera external gate status.

## Regla de invalidación

Si un input cambia (por ejemplo taxonomía), se invalidan dataset mapping, model head, thresholds, acceptance metrics y cualquier build que dependa de ellos. El handoff no copia evidencia: referencia IDs/hashes del ledger.