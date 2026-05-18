"""Ejecuta la simulación base del ABM de dependencia."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from abm_dependencia.model import DependencyABM
from abm_dependencia.utils import ensure_directory


def main() -> None:
    """Ejecuta 60 meses con 10.000 agentes y guarda un CSV."""
    model = DependencyABM(n_agents=10000, seed=42)
    model.run_model(n_months=60)
    results = model.get_results()

    output_dir = ensure_directory(PROJECT_ROOT / "outputs" / "runs")
    output_path = output_dir / "base_simulation.csv"
    results.to_csv(output_path, index=False)

    print("Primeras filas:")
    print(results.head())
    print("\nUltimas filas:")
    print(results.tail())
    print(f"\nCSV generado: {output_path}")


if __name__ == "__main__":
    main()
