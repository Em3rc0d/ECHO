# Training Plan — MK1

## Stage 0 — zero/frozen baseline

Evaluar scores directos o embeddings preentrenados sin fine-tuning para establecer piso.

## Stage 1 — frozen encoder + ECHO head

Entrenar head sobre manifest ECHO; class weights/sampling se comparan si hay imbalance.

## Stage 2 — selective fine-tuning

Sólo si Stage 1 no alcanza criterios. Descongelar parcialmente con LR menor y early stopping.

## Data augmentation candidate

background mixing, gain, time shift y ruido representativo. Pitch/time-stretch sólo si no destruye identidad de la clase. Toda augmentation tiene versión.

## Hard-negative loop

Recolectar falsos positivos del holdout/field set, etiquetar y añadirlos a entrenamiento siguiente sin contaminar el test final.

## Reproducibilidad

Registrar seed, optimizer, LR schedule, epochs, checkpoint checksum, dataset manifest y preprocessing version.