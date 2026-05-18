# Resumen de continuidad del proyecto

## Contexto

Proyecto: `ABM-ML-Dependencia`

TFM sobre un modelo basado en agentes para simular de forma simplificada el sistema de atención a la dependencia. El objetivo actual es tener una base ABM clara, reproducible y defendible, y preparar datasets sintéticos para modelos sustitutos posteriores.

La validación empírica contra indicadores externos como el IMCV queda para una fase posterior. Las métricas actuales son descriptivas e internas del ABM.

## Modelo ABM actual

El modelo simula el flujo administrativo simplificado del SAAD:

```text
poblacion vulnerable / no solicitante
-> pendiente de grado
-> con derecho reconocido
-> con PIA
-> prestacion efectiva o lista de espera
```

También registra:

- grados: `grado_I`, `grado_II`, `grado_III`
- prestaciones: `teleasistencia`, `ayuda_domicilio`, `atencion_residencial`, `cuidados_familiares`

La población vulnerable inicial coherente es de `6387` agentes. En el mes 0, `no_solicitantes` también vale `6387`.

## Estructura principal

```text
src/
├── model/
│   ├── agents.py
│   ├── model.py
│   └── parameters.py
├── analysis/
│   ├── plots.py
│   └── metrics.py
├── datasets/
│   ├── scenario_sampler.py
│   ├── mlp_exporter.py
│   ├── graph_exporter.py
│   └── split_generator.py
├── run_simulation.py
└── run_experiments.py
```

`src/abm_dependencia/` se mantiene como capa de compatibilidad con la primera versión del proyecto.

## Comandos importantes

Ejecutar simulación base:

```powershell
python -m src.run_simulation
```

Generar datasets sintéticos para MLP y GNN:

```powershell
python -m src.run_experiments
```

Ejecutar tests:

```powershell
python -m pytest
```

## Salidas actuales

Simulación base:

```text
data/simulation_outputs/base_simulation.csv
outputs/figures/evolucion_estados_saad.png
outputs/figures/evolucion_grados_dependencia.png
outputs/figures/evolucion_prestaciones.png
outputs/figures/evolucion_estados_finales.png
outputs/metrics/base_simulation_metrics.json
```

Datasets sintéticos:

```text
outputs/datasets/simulation_parameters.csv
outputs/datasets/mlp_dataset.csv
outputs/datasets/dataset_splits.csv
outputs/datasets/graphs/nodes.csv
outputs/datasets/graphs/edges.csv
outputs/datasets/graphs/graph_targets.csv
```

## API relevante

Uso esperado del modelo:

```python
from src.model.parameters import get_base_parameters
from src.model.model import DependenceABM

params = get_base_parameters()
model = DependenceABM(parameters=params)
df = model.run()
```

`get_base_parameters()` devuelve una copia independiente de los parámetros base.

## Datasets para modelos sustitutos

La MLP usará:

```text
outputs/datasets/mlp_dataset.csv
```

La GNN usará:

```text
outputs/datasets/graphs/nodes.csv
outputs/datasets/graphs/edges.csv
outputs/datasets/graphs/graph_targets.csv
```

Principio metodológico:

- cada simulación tiene un `simulation_id` único
- MLP y GNN proceden de las mismas simulaciones ABM
- ambas representaciones comparten los mismos targets
- el split `train`/`validation`/`test` se hace por `simulation_id`

En la última generación por defecto:

- simulaciones: `100`
- filas MLP: `100`
- nodos: `1600`
- aristas: `1500`
- splits: `train=70`, `validation=15`, `test=15`

## Targets comunes MLP/GNN

```text
target_rate_prestacion_efectiva
target_rate_lista_espera
target_rate_sin_grado
target_final_prestacion_efectiva
target_final_lista_espera
target_final_sin_grado
target_month_prestacion_effectiva_exceeds_no_solicitantes
```

## Estado de verificación

Última verificación realizada:

- `python -m src.run_simulation` funciona
- `python -m src.run_experiments` funciona
- MLP y GNN comparten `simulation_id`
- los targets coinciden entre `mlp_dataset.csv` y `graph_targets.csv`
- los splits se hacen por `simulation_id`
- tests: `3 passed`

## Restricciones metodológicas actuales

Todavía no se debe añadir:

- entrenamiento de MLP
- entrenamiento de GNN
- PyTorch
- PyTorch Geometric
- TensorFlow
- DiffPool
- calibración automática
- MAE / RMSE contra datos externos
- comparación con IMCV
- interfaz web

La fase actual consiste en consolidar la implementación ABM y preparar datasets sintéticos trazables para entrenamiento posterior.

## Próximos pasos probables

1. Revisar si los rangos de perturbación de escenarios son metodológicamente defendibles.
2. Añadir documentación breve sobre el significado de nodos y aristas del grafo.
3. Añadir tests de esquema para los CSV generados.
4. Preparar notebooks de inspección de `mlp_dataset.csv` y de las tablas de grafo.
5. Solo después, iniciar modelos sustitutos MLP/GNN.
