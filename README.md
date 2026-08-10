# ABM-ML-Dependencia

Simulación basada en agentes (Mesa) del flujo administrativo del **SAAD** y pipeline para una **comparativa de modelos sustitutos (surrogates)** en el marco del TFM:

> *Modelos híbridos: ABM y Machine Learning para la evaluación de políticas públicas en dependencia y bienestar subjetivo.*

**Repositorio:** https://github.com/loritobad/ABM-ML-Dependencia

---

## Principio metodológico (orden obligatorio)

1. **Validar el ABM frente al IMCV** (`python -m src.run_imcv_validation`) — puerta empírica.
2. **Diseñar escenarios con LHS**, ejecutar réplicas y construir el dataset sintético.
3. **Comparar surrogates** (Dummy, Ridge, CART, RF/GBM, MLP) midiendo fidelidad al ABM, aceleración y capacidad de extrapolación.

El *ground truth* de los surrogates son las **salidas del ABM**, no los microdatos reales.

```text
surrogate  →  ABM  →  realidad (IMCV)
```

---

## Simulación base

```text
población vulnerable / no solicitante
  → pendiente de grado
  → sin grado | con derecho
                 → con PIA
                   → prestación efectiva | lista de espera
```

| Parámetro | Valor |
|-----------|------:|
| Población vulnerable inicial | 6387 |
| Horizonte | 60 meses |
| Salida | CSV **mensual agregado** |
| Archivo | `data/simulation_outputs/base_simulation.csv` |
| Proxy de bienestar | `wellbeing_proxy` (`src/analysis/wellbeing.py`) |

---

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Dependencias principales: `mesa`, `pandas`, `numpy`, `matplotlib`, `scikit-learn`, `scipy`, `pytest`.

---

## Comandos principales

```powershell
# 1) Simulación base + métricas (+ figuras)
python -m src.run_simulation

# 2) Puerta ABM ↔ IMCV
python -m src.run_imcv_validation

# 3) Dataset LHS × réplicas + hold-out de extrapolación
python -m src.run_experiments --method lhs --n-simulations 100 --n-extrapolation 15 --n-replicas 10

# Equivalente
python scripts/run_scenarios.py --n-simulations 100 --n-replicas 10

# 4) Scaffold de surrogates (bloquea si la puerta no pasa)
python -m src.surrogates.train

# Tests
python -m pytest
```

---

## Estructura del repositorio

```text
src/
├── model/                  # ABM Mesa (agentes, parámetros, modelo)
├── analysis/               # métricas, wellbeing, IMCV, plots
├── datasets/               # LHS, bounds, exporters, splits
├── surrogates/             # catálogo + scaffold de entrenamiento
├── run_simulation.py
├── run_imcv_validation.py
└── run_experiments.py
data/
├── raw/imcv_reference.csv              # plantilla IMCV (sustituir por oficiales INE)
└── simulation_outputs/base_simulation.csv
outputs/
├── metrics/base_simulation_metrics.json
├── metrics/abm_imcv_validation.json
└── datasets/                           # mlp_dataset, splits, manifest+SHA256, graphs/
docs/
└── metodologia.md
```

---

## Dataset sintético

| Concepto | Detalle |
|----------|---------|
| Unidad experimental | Escenario (`scenario_id` / `simulation_id`) |
| Target principal | `target_wellbeing_proxy` |
| Targets secundarios | Cobertura asistencial y lista de espera |
| Varianza intra-escenario | Columnas `std_*` (suelo de error irreducible) |
| Particiones | `train` / `validation` / `test` / `extrapolation` |
| Versionado | `outputs/datasets/dataset_manifest.json` (SHA256) |

---

## Estado actual

| Bloque | Estado |
|--------|--------|
| ABM base + métricas internas | Listo |
| Proxy de bienestar | Listo |
| Puerta IMCV (código + plantilla) | Listo — falta cargar IMCV oficial y cerrar decisión |
| LHS + réplicas + hash + split de extrapolación | Listo en código |
| Entrenamiento/evaluación completa de surrogates | Scaffold (siguiente incremento) |
| Prototipo web | Pendiente |

Documentación metodológica: [`docs/metodologia.md`](docs/metodologia.md).

---

## Licencia

Ver [`LICENSE`](LICENSE).
