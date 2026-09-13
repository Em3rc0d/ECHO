# MK1 Data Plan

## Sources

1. FSD50K filtered subset where license permits intended use.
2. ESC-50 / UrbanSound8K primarily as academic benchmark/reference where NC applies.
3. AudioSet ontology/mappings and pretrained models, not blind redistribution.
4. Optional SONYC/DCASE for multilabel/SED methodology.
5. ECHO field recordings as soon as camera/environment access exists.

## Canonical manifest

```csv
clip_id,path_ref,sha256,labels,source_dataset,asset_license,
original_recording_id,session_id,site_id,source_id,mic_id,
distance_m,snr_db,split
```

## QC

Reject/flag:

```text
corrupt audio
clipped unusable audio
wrong sample metadata
missing license
ambiguous label
unknown provenance
leakage group conflict
```

## Augmentation candidates

Train only:

```text
gain
background mix
reverb
mild time stretch
mild pitch shift
time/frequency masking
codec degradation
wind/noise
AGC/clipping simulation
```

Cada augmentation debe poder desactivarse y quedar registrada en training config.