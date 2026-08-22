# Metodología del ABM (alineada con la ruta del Capítulo 4)

## Principio rector

Hay dos preguntas distintas y un orden obligatorio:

1. **¿Es el ABM plausible frente a la realidad?** → validación ABM ↔ tasas SAAD (`python -m src.run_saad_validation`).
2. **¿Qué surrogate imita mejor al ABM?** → comparativa CART / RF-GBM / MLP (+ baselines), solo después de la puerta.

Cadena de incertidumbre: surrogate → ABM → realidad (tasas SAAD / IMSERSO). El IMCV queda archivado como puerta; `wellbeing_proxy` es el target de los surrogates.

## Representación del modelo

Modelo Mesa (**mapeo operativo v1.5**) con ticks mensuales del circuito SAAD:

`no_solicitante → pendiente_grado → (sin_grado | con_derecho → con_pia → prestacion_efectiva | lista_espera)`

- Agente: estado SAAD, grado, prestación, `grupo_edad`, `vulnerabilidad_sanitaria`, `salud_autopercibida`.
- Delays: `meses_min_pendiente_grado` (≈8), `meses_min_tramite_prestacion` (≈3).
- Prestaciones: **ocho** categorías (Tabla 12) mapeadas a **tres colas** (residencial, día, resto) más techo `cupo_atendidas`.
- Post-PIA: entra si hay hueco; si no, lista FIFO. No se usa el dado 98,41 %.
- Escala: `cupo_sim = stock_SAAD × N / 2.165.648` (solicitudes IMSERSO 31/12/2024).
- Contrato: `tema/mapeo-operativo-4.4.md` (workspace TFM).

Salida operativa: **CSV mensual agregado** (`data/simulation_outputs/base_simulation.csv`), no panel agente-mes.

## Proxy de bienestar

`src/analysis/wellbeing.py` define `wellbeing_proxy` (escala ~0–10) a partir de cobertura, lista de espera, sin grado y peso del grado III. Es el **target principal** de los surrogates. **No** es la puerta empírica.

## Validación empírica (puerta SAAD)

- Referencia: `data/raw/saad_reference.csv` (cobertura 91,30 % y limbo 8,70 % sobre *con derecho*, 31/12/2024).
- Cupos: `data/raw/saad_capacity_reference.csv`.
- Módulo: `src/analysis/saad_validation.py`
- Informe: `outputs/metrics/abm_saad_validation.json`
- Umbrales: MAE ≤ 5 pp `pasa`; ≤ 7,5 pp `pasa_con_reservas`; si no `no_pasa`.
- Corrida `seed=42` v1.5: MAE **3,09 pp**, decisión **`pasa`**.

El código IMCV permanece en el repo como archivo histórico; no decide el entrenamiento.

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
El entrenamiento completo (CV anidada, multi-semilla, Friedman/Nemenyi) es el siguiente incremento; `src/surrogates/train.py` bloquea si la puerta SAAD no está en pasa/pasa_con_reservas.

## Limitaciones actuales

- Sin microdatos individuales ni heterogeneidad territorial completa en el ABM.
- Las colas de tipo no saturan; el limbo emerge del techo nacional de atendidas.
- El dataset LHS×réplicas aún no está regenerado sobre v1.5.
- El entrenamiento comparativo de surrogates aún no está cerrado en código.
