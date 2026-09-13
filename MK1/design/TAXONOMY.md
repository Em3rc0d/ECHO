# MK1 Acoustic Taxonomy

## Principio

La clase describe una firma acústica, no una interpretación social.

## Candidatos

| Label | Qué significa | Confusores esperables | Estado |
|---|---|---|---|
| ALARM_SIREN | patrón de alarma/sirena | beeps, música tonal, reverse beeper | CANDIDATE |
| HORN | bocina/claxon | alarms, tonal machinery | CANDIDATE |
| GLASS_BREAK | rotura/fragmentación de vidrio | metal/ceramic impacts | CANDIDATE |
| IMPACT_CRASH | impacto/choque acústico fuerte | door slam, rock/metal impact | CANDIDATE |
| YELL_SCREAM | vocalización humana fuerte | speech, cheering, laughter | CANDIDATE |
| REVERSING_BEEPER | beeps repetitivos de reversa | alarms, electronic beeps | CANDIDATE |
| TIRE_SCREECH | fricción/chirrido de neumático | metal squeal, brakes, machinery | OPTIONAL |
| BACKGROUND_NO_TARGET | contexto sin target | infinito/heterogéneo | DESIGN STATE |
| UNKNOWN | ningún target con evidencia suficiente | todo lo fuera de distribución | DESIGN STATE |

## Selección final

Para entrar a MK1/build, cada target debe cumplir:

```text
>= data mínima razonable
+ license path conocida
+ confusores identificados
+ mapping consistente entre datasets
+ valor dentro de promesa ECHO
+ test protocol posible
```

## Multi-label

Contrato: vector de probabilidades por clase. No asumir exclusividad mutua.

Ejemplo:

```json
{
  "ALARM_SIREN": 0.91,
  "HORN": 0.08,
  "IMPACT_CRASH": 0.03
}
```

`UNKNOWN` no necesariamente es una neurona entrenada; puede ser un estado del decision layer cuando no existe evidencia suficiente.