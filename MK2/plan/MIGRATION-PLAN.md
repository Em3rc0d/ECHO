# Migration Plan — MK2

Cambios en schemas, taxonomy, event-engine state o storage requieren migración explícita.

## Principles

- backward-compatible readers durante ventana de transición;
- versioned topics o envelopes cuando sea necesario;
- no reescribir eventos históricos con taxonomía nueva;
- persistir versión original de modelo/taxonomy;
- dry-run antes de migration destructiva;
- rollback plan probado.

Metadata histórica debe seguir interpretable aun cuando una clase se renombre/depreque.