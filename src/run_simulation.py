"""Ejecuta la simulación base y genera sus salidas reproducibles."""

from __future__ import annotations

from pathlib import Path

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
    """Ejecuta 60 meses de simulación base y exporta CSV y figuras."""
    parameters = get_base_parameters()
    model = DependenciaABM(parameters=parameters, seed=42)
    model.run_model(parameters["simulation_months"])
    results = model.get_results()

    SIMULATION_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(SIMULATION_OUTPUT, index=False)

    plot_estados_saad(results, FIGURES_DIR / "evolucion_estados_saad.png")
    plot_grados_dependencia(results, FIGURES_DIR / "evolucion_grados_dependencia.png")
    plot_prestaciones(results, FIGURES_DIR / "evolucion_prestaciones.png")
    plot_estados_finales(results, FIGURES_DIR / "evolucion_estados_finales.png")

    metrics = calculate_simulation_metrics(results)
    save_metrics(metrics, METRICS_OUTPUT)

    print(f"CSV generado: {SIMULATION_OUTPUT}")
    print(f"Figuras generadas en: {FIGURES_DIR}")
    print(f"Metricas generadas: {METRICS_OUTPUT}")


if __name__ == "__main__":
    main()
