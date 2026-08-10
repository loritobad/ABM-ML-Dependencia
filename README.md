# ABM-ML-Dependencia

Modelo basado en agentes (Mesa) para simular, de forma simplificada y reproducible, el flujo administrativo del SAAD y preparar una **comparativa de modelos sustitutos** (surrogates) alineada con el TFM.

Repo: https://github.com/loritobad/ABM-ML-Dependencia

## Principio metodológico (orden obligatorio)

1. Validar el ABM frente al IMCV (`python -m src.run_imcv_validation`) — puerta empírica.
2. Diseñar escenarios con **LHS**, ejecutar réplicas y construir el dataset sintético.
3. Comparar surrogates (**Dummy, Ridge, CART, RF/GBM, MLP**) midiendo fidelidad al ABM, aceleración y extrapolación.

El ground truth de los surrogates son las salidas del ABM, no los microdatos reales. La cadena es: **surrogate → ABM → realidad (IMCV)**.

## Simulación base

```text
poblacion vulnerable / no solicitante
-> pendiente de grado
-> con derecho reconocido
-> con PIA
-> prestacion efectiva o lista de espera
```

- Población vulnerable inicial: **6387** agentes  
- Horizonte: **60** meses  
- Salida: CSV **mensual agregado** en `data/simulation_outputs/base_simulation.csv`  
- Proxy de bienestar: `wellbeing_proxy` (ver `src/analysis/wellbeing.py`)

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Comandos principales

```powershell
# Simulación base + métricas (+ figuras)
python -m src.run_simulation

# Puerta ABM ↔ IMCV (paso 1)
python -m src.run_imcv_validation

# Dataset LHS × réplicas + hold-out de extrapolación (pasos 2–4)
python -m src.run_experiments --method lhs --n-simulations 100 --n-extrapolation 15 --n-replicas 10

# Equivalente vía scripts/
python scripts/run_scenarios.py --n-simulations 100 --n-replicas 10

# Scaffold de surrogates (bloquea si la puerta no pasa)
python -m src.surrogates.train

# Tests
python -m pytest
```

## Estructura relevante

```text
src/
├── model/                 # ABM Mesa
├── analysis/              # métricas, wellbeing, IMCV, plots
├── datasets/              # LHS, bounds, exporters, splits
├── surrogates/            # catálogo + scaffold de entrenamiento
├── run_simulation.py
├── run_imcv_validation.py
└── run_experiments.py
data/
├── raw/imcv_reference.csv           # plantilla IMCV (sustituir por oficiales)
└── simulation_outputs/base_simulation.csv
outputs/
├── metrics/base_simulation_metrics.json
├── metrics/abm_imcv_validation.json
└── datasets/                        # mlp_dataset, splits, manifest+SHA256, graphs/
```

## Dataset sintético

- Unidad experimental: **escenario** (`scenario_id` / `simulation_id`).  
- Target principal: `target_wellbeing_proxy`.  
- Secundarios: cobertura y lista de espera.  
- `std_*`: varianza intra-escenario (suelo de error irreducible).  
- Splits: `train` / `validation` / `test` / `extrapolation`.  
- Manifest: `outputs/datasets/dataset_manifest.json` (incluye SHA256).

## Estado actual

| Bloque | Estado |
|--------|--------|
| ABM base + métricas internas | Listo |
| Proxy bienestar | Listo |
| Puerta IMCV (código + plantilla) | Listo — falta cargar IMCV oficial y cerrar decisión |
| LHS + réplicas + hash + split extrapolación | Listo en código |
| Entrenamiento/evaluación surrogates completa | Scaffold (siguiente incremento) |
| Prototipo web | Pendiente |

Documentación metodológica ampliada: `docs/metodologia.md`.
