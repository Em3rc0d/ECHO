# SLO Catalog — MK2

Los valores numéricos se completan después de capacity benchmark.

| SLI | Definición | Target | Estado |
|---|---|---|---|
| capture-to-event p95 | captura -> confirmed event | TBD | OPEN |
| publish p95 | confirmed -> broker ack | TBD | OPEN |
| source availability | tiempo HEALTHY por source | TBD | OPEN |
| false alarms/hour | por clase/site | TBD | OPEN |
| miss rate | por clase/condición | TBD | OPEN |
| recovery time | disconnect -> healthy | TBD | OPEN |
| max backlog | segundos/windows | bounded | DECISION_CANDIDATE |
| event duplicate rate | después de consumer dedup | TBD | OPEN |

Un SLO sólo puede certificarse para una combinación de hardware, modelo, config y workload definida.