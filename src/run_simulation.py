"""Ejecuta la simulación base y genera sus salidas reproducibles."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

try:
    from .analysis.metrics import calculate_simulation_metrics, save_metrics
    from .analysis.plots import (
        plot_estados_finales,
        plot_estados_saad,
        plot_grados_dependencia,
        plot_prestaciones,
    )
    from .model.model import DependenciaABM
    from .model.parameters import get_base_parameters
except ImportError:
    from analysis.metrics import calculate_simulation_metrics, save_metrics
    from analysis.plots import (
        plot_estados_finales,
        plot_estados_saad,
        plot_grados_dependencia,
        plot_prestaciones,
    )
    from model.model import DependenciaABM
    from model.parameters import get_base_parameters


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_OUTPUT = PROJECT_ROOT / "data" / "simulation_outputs" / "base_simulation.csv"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
METRICS_OUTPUT = PROJECT_ROOT / "outputs" / "metrics" / "base_simulation_metrics.json"


def main() -> None:
    """Ejecuta la simulación base (parámetros desde .env si existen) y exporta salidas."""
    if load_dotenv is not None:
        load_dotenv(PROJECT_ROOT / ".env")

    parameters = get_base_parameters()
    if os.getenv("ABM_SIMULATION_MONTHS"):
        parameters["simulation_months"] = int(os.environ["ABM_SIMULATION_MONTHS"])
    if os.getenv("ABM_INITIAL_VULNERABLE_POPULATION"):
        parameters["initial_vulnerable_population"] = int(
            os.environ["ABM_INITIAL_VULNERABLE_POPULATION"]
        )
    seed = int(os.getenv("ABM_SEED", "42"))

    model = DependenciaABM(parameters=parameters, seed=seed)
    model.run_model(parameters["simulation_months"])
    results = model.get_results()

    SIMULATION_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(SIMULATION_OUTPUT, index=False)

    plot_estados_saad(results, FIGURES_DIR / "evolucion_estados_saad.png")
    plot_grados_dependencia(results, FIGURES_DIR / "evolucion_grados_dependencia.png")
    plot_prestaciones(results, FIGURES_DIR / "evolucion_prestaciones.png")
    plot_estados_finales(results, FIGURES_DIR / "evolucion_estados_finales.png")

    metrics = calculate_simulation_metrics(results)
    metrics["seed"] = seed
    metrics["mapeo_version"] = os.getenv("ABM_MAPEO_VERSION", "v1")
    save_metrics(metrics, METRICS_OUTPUT)

    print(f"CSV generado: {SIMULATION_OUTPUT}")
    print(f"Figuras generadas en: {FIGURES_DIR}")
    print(f"Metricas generadas: {METRICS_OUTPUT}")
    print(
        "Resumen mes final: "
        f"prestacion={metrics['final_prestacion_efectiva']} "
        f"lista={metrics['final_lista_espera']} "
        f"sin_grado={metrics['final_sin_grado']} "
        f"no_sol={metrics['final_no_solicitantes']} "
        f"wellbeing={metrics['wellbeing_proxy']:.3f}"
    )


if __name__ == "__main__":
    main()
