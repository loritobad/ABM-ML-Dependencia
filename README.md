# ABM-ML-Dependencia

Implementación experimental en Python de un modelo basado en agentes para estudiar el circuito de dependencia en España y preparar, en fases posteriores, datos sintéticos para modelos sustitutos de Machine Learning.

El proyecto forma parte de un Trabajo Fin de Máster sobre modelos híbridos ABM y Machine Learning para la evaluación de políticas públicas en dependencia y bienestar subjetivo.

## Objetivo del modelo

La primera meta es construir un ABM mínimo, reproducible y fácil de explicar. Cada agente representa una persona mayor de 65 años que puede ser vulnerable, solicitar valoración de dependencia, recibir grado, obtener PIA, acceder a una prestación efectiva o quedar en lista de espera.

La simulación avanza por meses y genera un CSV con salidas agregadas para análisis descriptivo y futuros escenarios de política pública.

## Estructura del repositorio

```text
ABM-ML-Dependencia/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── abm_dependencia/
│       ├── __init__.py
│       ├── agent.py
│       ├── model.py
│       ├── parameters.py
│       ├── collectors.py
│       ├── experiments.py
│       └── utils.py
├── scripts/
│   ├── run_base_simulation.py
│   ├── run_scenarios.py
│   └── generate_plots.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── synthetic/
├── outputs/
│   ├── runs/
│   ├── figures/
│   └── reports/
├── notebooks/
│   └── exploratory_analysis.ipynb
└── docs/
    └── metodologia.md
```

## Instalación

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución de la simulación base

```powershell
python scripts/run_base_simulation.py
```

Este comando ejecuta 60 meses con 10.000 agentes y guarda:

```text
outputs/runs/base_simulation.csv
```

El script imprime por consola las primeras filas, las últimas filas y la ruta del CSV generado.

## Generación de gráficos

Después de ejecutar la simulación base:

```powershell
python scripts/generate_plots.py
```

Se generan tres figuras en `outputs/figures/`:

- `evolucion_estados_saad.png`
- `evolucion_grados_dependencia.png`
- `evolucion_prestaciones.png`

## Salidas esperadas

El CSV mensual incluye variables agregadas como:

- población vulnerable
- estados administrativos SAAD
- grados de dependencia I, II y III
- prestaciones seleccionadas

Estas salidas están preparadas para ser ampliadas después con escenarios, calibración, análisis de sensibilidad y modelos sustitutos de Machine Learning.

## Nota

Esta es una primera versión experimental del ABM para el TFM.
