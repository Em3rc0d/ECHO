# Quarry — Hard Negatives

Candidatos iniciales:

- portazo vs collision/impact;
- platos/metal vs glass break;
- música/tonos vs siren/alarm;
- voces excitadas/canto vs scream/shout;
- brakes/mechanical squeal vs tire squeal;
- traffic bed vs horn.

Proceso: mine false positives -> human review -> add to train/validation according to split policy -> rerun regression. El test final permanece cerrado.