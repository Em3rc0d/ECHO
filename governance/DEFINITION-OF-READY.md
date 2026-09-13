# Definition of Ready — MK1 Build

MK1/build puede pasar de `GATED` a `READY` cuando:

- [ ] MK0 está certificado.
- [ ] Promesa y scope IN/OUT congelados.
- [ ] Clases MK1 finales aprobadas.
- [ ] Label mapping documentado.
- [ ] Hard negatives definidos.
- [ ] Dataset registry y license checks definidos.
- [ ] Split policy group-aware congelada.
- [ ] Benchmark A/B/C definido.
- [ ] Source abstraction congelada.
- [ ] Pipeline de audio definido.
- [ ] `RAW_INFERENCE -> CANDIDATE_EVENT -> CONFIRMED_EVENT -> ALERT` definido.
- [ ] Event schema versionado.
- [ ] MQTT topics/payload/QoS candidate congelados para build.
- [ ] Secrets policy definida.
- [ ] Observability mínima definida.
- [ ] Test plan preparado antes de escribir producto.
- [ ] Acceptance targets etiquetados como `TARGET`, no como resultados.
- [ ] External gates necesarios para la vertical resueltos o existe simulador/replay autorizado equivalente.
- [ ] No queda ninguna decisión `OPEN` que obligue a rediseñar componentes core.

`EXTERNAL_GATE_OPEN` no bloquea documentación, pero sí bloquea cualquier test que pretenda certificar comportamiento de hardware real.