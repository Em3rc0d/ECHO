# Sources — Datasets

| Dataset | Evidencia | Riesgo/licencia | URL |
|---|---|---|---|
| AudioSet | ~2.08M segmentos de 10 s; 527 labels en sitio actual; ontología jerárquica | clips referencian YouTube; disponibilidad mutable; revisar términos | https://research.google.com/audioset/dataset/index.html |
| FSD50K | 51,197 clips, 200 clases, 108.3 h, weak multi-label | dataset CC-BY pero assets mezclan CC0/CC-BY/CC-BY-NC/Sampling+ | https://zenodo.org/records/4060432 |
| ESC-50 | 2,000 clips, 50 clases, 5 s, incluye siren/car horn | dataset CC BY-NC; ESC-10 CC BY | https://github.com/karolpiczak/ESC-50 |
| DCASE/DESED | SED con weak/strong/synthetic subsets y timestamps en subsets fuertes | dominio doméstico; no asumir transferencia urbana | https://dcase.community/challenge2021/task-sound-event-detection-and-separation-in-domestic-environments |
| UrbanSound8K | benchmark urbano candidato | verificar licencia/metadata exacta antes de ingestión | https://urbansounddataset.weebly.com/urbansound8k.html |
| SONYC-UST | urban sound tagging candidato | verificar versión/licencia exacta | https://zenodo.org/communities/sonyc |

## Regla ECHO

La selección se hace a nivel de **asset + licencia + provenance**. FSD50K es especialmente útil para diversidad y mapeo AudioSet, pero sus licencias por clip impiden tratar todos los assets como equivalentes.