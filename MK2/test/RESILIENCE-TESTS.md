# Resilience Tests — MK2

- camera disconnect/reconnect repetido;
- broker restart;
- network partition parcial;
- decoder process crash;
- model worker crash;
- storage unavailable/full;
- corrupted config;
- slow subscriber;
- burst de eventos simultáneos;
- one noisy/flapping source junto a sources sanos.

Criterio: aislamiento, recuperación observable, buffers acotados y ausencia de corrupción/duplicación lógica no controlada.