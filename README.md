# ABM-ML-Dependencia

Modelo basado en agentes para simular, de forma simplificada y reproducible, el flujo administrativo del sistema de atencion a la dependencia. El proyecto se desarrolla como base metodologica de un TFM y prioriza claridad, trazabilidad y estructura academica antes que complejidad computacional.

## Objetivo del proyecto

El objetivo actual es disponer de una simulacion base defendible del circuito SAAD:

```text
poblacion vulnerable / no solicitante
-> pendiente de grado
-> con derecho reconocido
-> con PIA
-> prestacion efectiva o lista de espera
```

La simulacion genera resultados mensuales agregados para revisar dinamicas del modelo, documentar supuestos y preparar fases posteriores de validacion. La validacion empirica final no se plantea directamente contra SAAD, sino contra indicadores externos como el IMCV; los datos SAAD se usan para parametrizar y justificar rangos plausibles.

## Descripcion del modelo

Cada agente representa una persona vulnerable que inicialmente no ha solicitado valoracion. En cada tick mensual puede avanzar por los estados administrativos del modelo segun probabilidades configuradas en `src/model/parameters.py`.

El modelo registra cada mes:

- estados SAAD: no solicitantes, pendiente de grado, sin grado, con derecho, con PIA, prestacion efectiva y lista de espera
- grados de dependencia: grado I, grado II y grado III
- prestaciones: teleasistencia, ayuda a domicilio, atencion residencial y cuidados familiares

La simulacion base parte de una poblacion vulnerable inicial coherente de 6.387 agentes, definida de forma unica con `initial_vulnerable_agents = 6387`. Por coherencia, en el mes 0 los agentes `no_solicitantes` tambien son 6.387.

## Estructura del repositorio

```text
ABM-ML-Dependencia/
├── data/
│   ├── raw/
│   ├── processed/
│   └── simulation_outputs/
│       └── base_simulation.csv
├── notebooks/
│   └── exploratory_analysis.ipynb
├── outputs/
│   ├── figures/
│   │   ├── evolucion_estados_saad.png
│   │   ├── evolucion_grados_dependencia.png
│   │   ├── evolucion_prestaciones.png
│   │   └── evolucion_estados_finales.png
│   ├── metrics/
│   │   └── base_simulation_metrics.json
│   └── datasets/
│       ├── simulation_parameters.csv
│       ├── mlp_dataset.csv
│       ├── dataset_splits.csv
│       └── graphs/
│           ├── nodes.csv
│           ├── edges.csv
│           └── graph_targets.csv
├── src/
│   ├── model/
│   │   ├── agents.py
│   │   ├── model.py
│   │   └── parameters.py
│   ├── analysis/
│   │   └── plots.py
│   ├── datasets/
│   │   ├── scenario_sampler.py
│   │   ├── mlp_exporter.py
│   │   ├── graph_exporter.py
│   │   └── split_generator.py
│   ├── run_simulation.py
│   └── run_experiments.py
├── requirements.txt
└── README.md
```

El paquete `src/abm_dependencia/` se mantiene como capa de compatibilidad con la primera version del proyecto y redirige al nuevo nucleo modular.

## Instalacion

Desde la raiz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecucion de la simulacion

```powershell
python -m src.run_simulation
```

El comando ejecuta la simulacion base durante 60 meses y genera:

```text
data/simulation_outputs/base_simulation.csv
outputs/figures/evolucion_estados_saad.png
outputs/figures/evolucion_grados_dependencia.png
outputs/figures/evolucion_prestaciones.png
outputs/figures/evolucion_estados_finales.png
outputs/metrics/base_simulation_metrics.json
```

## Generacion de datasets sinteticos

Para preparar datos de entrenamiento posteriores para modelos sustitutos, se pueden ejecutar multiples simulaciones ABM con variaciones suaves de parametros. Por defecto se ejecutan 100 simulaciones:

```powershell
python -m src.run_experiments
```

Este comando genera:

```text
outputs/datasets/simulation_parameters.csv
outputs/datasets/mlp_dataset.csv
outputs/datasets/dataset_splits.csv
outputs/datasets/graphs/nodes.csv
outputs/datasets/graphs/edges.csv
outputs/datasets/graphs/graph_targets.csv
```

La MLP usara `mlp_dataset.csv`. La GNN usara `nodes.csv`, `edges.csv` y `graph_targets.csv`. Ambas representaciones proceden de las mismas simulaciones ABM, comparten `simulation_id` y usan los mismos targets. La particion `train`/`validation`/`test` se realiza por `simulation_id`, no por filas individuales.

Esta fase solo prepara salidas sinteticas para entrenamiento posterior. No incluye todavia entrenamiento de MLP, GNN, calibracion automatica ni comparacion con IMCV.

Tambien pueden usarse las rutas historicas:

```powershell
python scripts/run_base_simulation.py
python scripts/generate_plots.py
```

## Notebook exploratorio

El notebook `notebooks/exploratory_analysis.ipynb` carga el CSV base, muestra las primeras filas, revisa columnas y estadisticos, comprueba la poblacion total simulada, resume los resultados finales y muestra las figuras principales.

## Advertencia metodologica

Los resultados actuales son una comprobacion funcional del ABM y una simulacion base exploratoria. No deben interpretarse como validacion empirica final, estimacion causal ni prediccion calibrada del sistema real. Las siguientes fases deberan incorporar contraste externo, analisis de sensibilidad, escenarios y justificacion empirica mas detallada.
