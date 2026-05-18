"""Regenera gráficos descriptivos a partir del CSV de simulación base."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from analysis.plots import (  # noqa: E402
    plot_estados_finales,
    plot_estados_saad,
    plot_grados_dependencia,
    plot_prestaciones,
)

INPUT_PATH = PROJECT_ROOT / "data" / "simulation_outputs" / "base_simulation.csv"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"No existe {INPUT_PATH}. Ejecuta primero: python src/run_simulation.py"
        )

    data = pd.read_csv(INPUT_PATH)
    plot_estados_saad(data, FIGURES_DIR / "evolucion_estados_saad.png")
    plot_grados_dependencia(data, FIGURES_DIR / "evolucion_grados_dependencia.png")
    plot_prestaciones(data, FIGURES_DIR / "evolucion_prestaciones.png")
    plot_estados_finales(data, FIGURES_DIR / "evolucion_estados_finales.png")

    print(f"Graficos generados en: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
