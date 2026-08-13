"""Pruebas del contrato mapeo operativo v1."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from model.parameters import BENEFIT_KEYS, DEFAULT_PARAMETERS, get_base_parameters  # noqa: E402
from model.model import DependenciaABM  # noqa: E402


def test_v1_has_eight_benefits() -> None:
    assert len(BENEFIT_KEYS) == 8
    dist = DEFAULT_PARAMETERS["distribucion_prestaciones"]
    assert set(dist) == set(BENEFIT_KEYS)
    assert abs(sum(dist.values()) - 1.0) < 1e-6


def test_v1_direct_grade_and_right() -> None:
    assert DEFAULT_PARAMETERS["prob_con_derecho"] == 0.8032
    assert DEFAULT_PARAMETERS["distribucion_grados"]["I"] == 0.3615


def test_v1_delays_and_health_context() -> None:
    p = get_base_parameters()
    assert p["meses_min_pendiente_grado"] == 8
    assert p["meses_min_tramite_prestacion"] == 3
    assert "65_74" in p["distribucion_grupos_edad"]
    assert p["pension_media_nacional"] == 1439.11
    assert p["prop_nacional_65"] == 0.2015


def test_v1_simulation_columns() -> None:
    model = DependenciaABM(
        parameters={"initial_vulnerable_population": 80, "simulation_months": 12},
        seed=7,
    )
    model.run_model(n_months=12)
    results = model.get_results()
    for key in BENEFIT_KEYS:
        assert key in results.columns
    assert "vuln_sanitaria" in results.columns
    agent = next(iter(model.agents))
    assert agent.grupo_edad in ("65_74", "75_84", "85_plus")
    assert agent.salud_autopercibida in ("favorable", "intermedia", "desfavorable")
