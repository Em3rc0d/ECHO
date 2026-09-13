# Model Evaluation — MK1

## Requisitos

- comparison manifest idéntico entre candidatos;
- métricas por clase + macro;
- confidence calibration;
- long-negative false alarm test;
- noisy/SNR slices;
- runtime benchmark warm/cold;
- artifact size y dependency footprint.

## Selection scorecard

No sumar métricas heterogéneas sin justificar pesos. Preferir Pareto analysis: calidad vs latencia vs footprint. Si dos modelos quedan cercanos, gana la opción operativamente más simple para MK1 y se conserva el challenger para MK2.