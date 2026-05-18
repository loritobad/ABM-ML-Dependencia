"""Pruebas básicas de ejecución del ABM."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from abm_dependencia.model import DependencyABM  # noqa: E402


def test_base_simulation_outputs_expected_columns() -> None:
    """El modelo mínimo ejecuta y devuelve las columnas agregadas básicas."""
    model = DependencyABM(n_agents=100, seed=42)
    model.run_model(n_months=3)
    results = model.get_results()

    expected_columns = {
        "month",
        "vulnerables",
        "pendiente_grado",
        "con_derecho",
        "con_pia",
        "prestacion_efectiva",
        "lista_espera",
    }

    assert not results.empty
    assert expected_columns.issubset(results.columns)
    assert results["month"].tolist() == [0, 1, 2, 3]
