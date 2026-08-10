# Metodología del ABM (alineada con la ruta del Capítulo 4)

## Principio rector

Hay dos preguntas distintas y un orden obligatorio:

1. **¿Es el ABM plausible frente a la realidad?** → validación ABM ↔ IMCV (`python -m src.run_imcv_validation`).
2. **¿Qué surrogate imita mejor al ABM?** → comparativa CART / RF-GBM / MLP (+ baselines), solo después de la puerta.

Cadena de incertidumbre: surrogate → ABM → realidad (IMCV).

## Representación del modelo

Modelo Mesa con ticks mensuales del circuito SAAD:

`no_solicitante → pendiente_grado → (sin_grado | con_derecho → con_pia → prestacion_efectiva | lista_espera)`

Salida operativa: **CSV mensual agregado** (`data/simulation_outputs/base_simulation.csv`), no panel agente-mes.

## Proxy de bienestar

`src/analysis/wellbeing.py` define `wellbeing_proxy` (escala ~0–10) a partir de cobertura, lista de espera, sin grado y peso del grado III. Es el **target principal** de los surrogates y el vínculo con el IMCV.

## Validación empírica (puerta)

- Referencia: `data/raw/imcv_reference.csv` (sustituir plantilla por valores oficiales INE).
- Módulo: `src/analysis/imcv_validation.py`
- Informe: `outputs/metrics/abm_imcv_validation.json`
- Métricas: Pearson, Spearman, MAE, RMSE, KS; decisión `pasa | pasa_con_reservas | no_pasa`.

## Escenarios y dataset sintético

- Muestreo por defecto: **Latin Hypercube Sampling** (`sample_lhs_scenarios`).
- Rangos: `src/datasets/parameter_bounds.py`.
- Por escenario: ≥10 réplicas; media + `std_*` (suelo de error irreducible).
- Splits por `scenario_id`: train / validation / test / **extrapolation**.
- Manifest + SHA256: `outputs/datasets/dataset_manifest.json`.

```powershell
python -m src.run_experiments --method lhs --n-replicas 10
python scripts/run_scenarios.py --n-simulations 100 --n-replicas 10
```

## Surrogates

Catálogo en `src/surrogates/`: Dummy, Ridge, CART, RandomForest, GradientBoosting/XGBoost, MLP.  
El entrenamiento completo (CV anidada, multi-semilla, Friedman/Nemenyi) es el siguiente incremento; `src/surrogates/train.py` bloquea si la puerta IMCV no está en pasa/pasa_con_reservas.

## Limitaciones actuales

- Sin microdatos individuales ni heterogeneidad territorial completa en el ABM.
- La referencia IMCV del repo es una **plantilla** hasta cargar cifras oficiales.
- El entrenamiento comparativo de surrogates aún no está cerrado en código.
