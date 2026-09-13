# MK0 / Test

## Objetivo

Test en MK0 significa **validar la calidad de las decisiones y evidencia**, no medir accuracy de un modelo todavía.

## Checks

- [ ] todas las fuentes clave tienen provenance;
- [ ] claims externos no se presentan como resultados propios;
- [ ] licencias críticas están registradas o marcadas OPEN;
- [ ] datasets se evaluaron por utilidad real, no solo nombre de clase;
- [ ] modelos se comparan con benchmark propio antes de elegir ganador;
- [ ] arquitectura soporta N sources conceptualmente;
- [ ] event lifecycle separa inference/event/alert;
- [ ] thresholds no fueron inventados;
- [ ] distancia no fue prometida sin medir;
- [ ] privacy scope excluye ASR/speaker ID;
- [ ] external gates están enumerados;
- [ ] risk register cubre domain shift, false alarms, RTSP y licensing;
- [ ] DoR de MK1 puede evaluarse objetivamente.

## Resultado

`PASS` certifica MK0. `FAIL` devuelve el grafo al artefacto upstream defectuoso.