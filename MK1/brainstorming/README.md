# MK1 / Brainstorming

## Pregunta

¿Cuál es la vertical mínima que demuestra que ECHO cumple su promesa sin esconder incertidumbres bajo una demo?

## Escenario de validación

Una fuente de audio entrega stream continuo. ECHO:

1. identifica `source_id`;
2. extrae y normaliza audio;
3. produce scores por ventana;
4. agrega temporalmente esos scores;
5. confirma un evento;
6. publica un mensaje estructurado;
7. conserva provenance suficiente para reproducir la decisión.

## Clases candidatas

Set candidato de 4–6 clases + no-target/unknown:

```text
ALARM_SIREN
HORN
GLASS_BREAK
IMPACT_CRASH
YELL_SCREAM
REVERSING_BEEPER
```

No se congelan todas automáticamente. La selección final depende de data, confusores, cámara/ambiente y valor de demostración.

## Demo válida

Una demo MK1 válida no es “reproducir un WAV y ver una etiqueta”. Debe mostrar:

```text
stream/replay continuo
+ event lifecycle
+ source identity
+ latency measured
+ false positives observed
+ Pub/Sub delivery
+ reproducibility metadata
```

## Demo inválida

- scores mostrados sin event aggregation;
- clips de train usados como test;
- thresholds elegidos para que la demo salga bonita;
- una sola clase fácil sin negativos;
- claim de distancia no medido;
- class label que infiere una situación que el audio no prueba.