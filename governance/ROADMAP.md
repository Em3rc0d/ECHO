# ECHO Roadmap

## Fase actual

```text
MK0 research/design closure
        ↓
external camera gates
        ↓
MK0 certification
        ↓
MK1 Definition of Ready
        ↓
MK1 build
        ↓
MK1 test/certification
        ↓
MK2 design freeze from MK1 evidence
        ↓
MK2 build/hardening
        ↓
MK2 release gate
```

## Immediate actions

1. cerrar taxonomía MK1 usando availability/licensing/confusors;
2. confirmar cámara con profesora;
3. congelar dataset manifest strategy;
4. congelar A/B/C benchmark protocol;
5. decidir licencia del código del proyecto;
6. completar MK0 gate;
7. recién entonces habilitar MK1/build.

## Regla

Nunca avanzar por calendario si el grafo de dependencias sigue abierto. Los pasos externos se marcan `EXTERNAL_GATE_OPEN` para que no parezcan olvidados.