# BUILD GATE — MK0

**Estado: GATED / NOT_STARTED**

MK0 no construye producto. La carpeta `build/` documenta únicamente qué artefactos experimentales podrán existir una vez cerrados design/arch/plan.

## Permitido después del gate

- scripts reproducibles de dataset manifest;
- harness de benchmark;
- probes de FFmpeg/RTSP;
- notebooks/CLI de análisis aislados;
- generación de checksums/manifests.

## No permitido todavía

- servicio ECHO definitivo;
- API productiva;
- dashboard;
- broker como dependencia arquitectónica congelada sin decisión;
- entrenamiento presentado como modelo final.

## Unlock

Sólo cuando `MK0/test/MK0-GATE.md` certifique el milestone y no existan nodos internos críticos `OPEN`.