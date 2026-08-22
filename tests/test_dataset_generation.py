"""Pruebas básicas de generación de datasets sintéticos."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from analysis.metrics import calculate_simulation_metrics  # noqa: E402
from analysis.wellbeing import estimate_wellbeing_proxy  # noqa: E402
from datasets.graph_exporter import build_graph_tables  # noqa: E402
from datasets.mlp_exporter import TARGET_COLUMNS, build_mlp_row  # noqa: E402
from datasets.scenario_sampler import sample_lhs_scenarios, sample_scenario  # noqa: E402
from datasets.split_generator import generate_splits  # noqa: E402
from model.model import DependenceABM  # noqa: E402
from model.parameters import get_base_parameters  # noqa: E402


def test_wellbeing_proxy_is_bounded() -> None:
    proxy = estimate_wellbeing_proxy(
        {
            "rate_prestacion_efectiva": 0.5,
            "rate_lista_espera": 0.2,
            "rate_sin_grado": 0.1,
            "rate_grado_III": 0.25,
        }
    )
    assert 0.0 <= proxy <= 10.0


def test_mlp_and_graph_exports_share_simulation_id_and_targets() -> None:
    parameters = sample_scenario(get_base_parameters(), random_seed=7)
    parameters["initial_vulnerable_population"] = 50
    parameters["simulation_months"] = 2

    model = DependenceABM(parameters=parameters, seed=7)
    results = model.run()
    metrics = calculate_simulation_metrics(results)

    assert "wellbeing_proxy" in metrics
    mlp_row = build_mlp_row(1, parameters, metrics, regime="interpolation", n_replicas=1)
    nodes, edges, graph_targets = build_graph_tables(1, results, metrics)

    assert mlp_row["simulation_id"] == graph_targets["simulation_id"]
    assert "target_wellbeing_proxy" in mlp_row
    assert all(mlp_row[key] == graph_targets[key] for key in TARGET_COLUMNS)
    assert len(nodes) == 20
    assert len(edges) == 19


def test_lhs_scenarios_are_reproducible() -> None:
    a = sample_lhs_scenarios(4, seed=123, regime="interpolation")
    b = sample_lhs_scenarios(4, seed=123, regime="interpolation")
    assert len(a) == 4
    assert a[0]["parameters"]["factor_capacidad"] == b[0]["parameters"][
        "factor_capacidad"
    ]
    assert a[0]["regime"] == "interpolation"


def test_lhs_v15_scales_cupos_not_dice() -> None:
    from model.capacity import cupos_from_n

    scenarios = sample_lhs_scenarios(8, seed=42, regime="interpolation")
    params = scenarios[0]["parameters"]
    assert "factor_capacidad" in params
    assert 0.80 <= params["factor_capacidad"] <= 1.20
    expected = cupos_from_n(params["initial_vulnerable_population"])
    factor = params["factor_capacidad"]
    assert params["cupo_atendidas"] == max(
        1, int(round(expected["cupo_atendidas"] * factor))
    )
    extra = sample_lhs_scenarios(5, seed=99, regime="extrapolation")
    assert extra[0]["parameters"]["factor_capacidad"] >= 0.55
    assert extra[0]["parameters"]["factor_capacidad"] <= 1.45


def test_splits_include_extrapolation_holdout() -> None:
    splits = generate_splits(
        list(range(1, 11)),
        random_seed=42,
        extrapolation_ids=[11, 12],
    )
    by_id = {row["simulation_id"]: row["split"] for row in splits}
    assert by_id[11] == "extrapolation"
    assert by_id[12] == "extrapolation"
    assert set(by_id[i] for i in range(1, 11)).issubset(
        {"train", "validation", "test"}
    )
