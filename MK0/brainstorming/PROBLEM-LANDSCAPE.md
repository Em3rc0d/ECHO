# Problem Landscape — MK0

## Promesa fija

> Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.

MK0 parte de un problema de percepción: el audio ambiental es continuo, ruidoso, no estructurado y dependiente del contexto. El valor de ECHO no está en «escuchar una cámara», sino en transformar señales acústicas en eventos observables, trazables y consumibles por otros sistemas.

## Problemas técnicos a investigar

1. **Audio tagging vs Sound Event Detection (SED).** El tagging responde qué sonidos aparecen en una ventana; SED añade localización temporal. ECHO puede comenzar con ventanas + agregación temporal, pero debe medir si esa aproximación produce latencia y falsas alarmas aceptables.
2. **Domain shift.** Modelos entrenados con AudioSet/Freesound no representan necesariamente micrófonos de cámaras, compresión AAC/G.711, reverberación, tráfico, viento ni distancias reales.
3. **Open world.** El ambiente contiene sonidos fuera de taxonomía. Un clasificador cerrado puede forzar desconocidos a una clase conocida; por eso `OTHER/BACKGROUND`, calibración y OOD son líneas obligatorias.
4. **Multi-label.** Dos eventos pueden coexistir. No se debe congelar softmax single-label sin comparar una salida multi-label/sigmoid cuando la taxonomía lo requiera.
5. **Temporalidad.** Una inferencia de ventana no equivale a un evento real. Se necesita una máquina temporal que confirme, agrupe, deduplique y rearme.
6. **Operación continua.** RTSP puede cortar, variar codec, introducir jitter o retrasos. ECHO debe separar fallos de captura, inferencia y entrega.

## Hipótesis de valor

- H1: un backbone preentrenado puede reducir el volumen de datos etiquetados necesario para una primera PoC.
- H2: los errores dominantes del producto surgirán más del dominio real y del Event Engine que del benchmark académico del backbone.
- H3: la arquitectura multi-source debe existir desde el contrato, aunque MK1 pruebe físicamente una sola fuente.
- H4: métricas por clip no bastan; `false alarms/hour`, miss rate y latencia end-to-end son métricas de producto.

Estas hipótesis son **CANDIDATE**, no decisiones.